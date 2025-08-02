"""
Run computer_use_demo.loop.sampling_loop inside the backend.

We expose one top-level coroutine `run_computer_use_session(session_id)`.
It:
  • pulls the full history from DB → List[BetaMessageParam]
  • feeds that into sampling_loop()
  • for every new block:
        – persists to DB (Message table, plus crude binary store for images)
        – pushes the JSON‐serialisable version onto the SSE queue
"""

from __future__ import annotations

import asyncio
import base64
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from anthropic.types.beta import (
    BetaContentBlockParam,
    BetaMessageParam,
    BetaToolResultBlockParam,
    BetaToolUseBlockParam,
)
from .computer_use_demo.loop import (
    sampling_loop,
    APIProvider,
    ToolVersion,
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .db import Message as DBMessage, async_session
from .state import queue_for
from .schemas import Message

# ----- small helper -----------------------------------------------------------------

MEDIA_ROOT = Path("./media")
MEDIA_ROOT.mkdir(exist_ok=True)

def _serialize_block(block: BetaContentBlockParam) -> Dict[str, Any]:
    """Make the block JSON serialisable (convert bytes/images)."""
    if block["type"] == "image":
        return block  # already base64
    if block["type"] == "tool_result":
        # ensure nested images are serialised
        safe = dict(block)
        safe["content"] = [_serialize_block(b) for b in block["content"]]
        return safe
    return block  # text, tool_use, thinking as-is


# ----- main runner ------------------------------------------------------------------

async def run_computer_use_session(session_id: str):
    """
    One execution per *user* turn. We assume somebody already appended the
    latest user Message to DB & queue, then scheduled this coroutine.
    """
    queue = queue_for(session_id)

    async with async_session() as db:
        # 1. hydrate history → BetaMessageParam list
        messages: List[BetaMessageParam] = []
        rows = await db.execute(
            select(DBMessage).where(DBMessage.session_id == session_id).order_by(DBMessage.id)
        )
        for m in rows.scalars():
            messages.append(
                {"role": m.role, "content": [{"type": "text", "text": m.content}]}
            )

    # 2. run Anthropic loop
    def output_cb(block: BetaContentBlockParam):
        asyncio.create_task(_store_and_push(session_id, block, queue))

    def tool_output_cb(tool_res, tool_use_id):
        # tool_res is already text + optional base64 image; wrap like sampling_loop does
        res_block: BetaToolResultBlockParam = {
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "content": [],
            "is_error": bool(tool_res.error),
        }
        if tool_res.output:
            res_block["content"].append({"type": "text", "text": tool_res.output})
        if tool_res.base64_image:
            res_block["content"].append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": tool_res.base64_image,
                    },
                }
            )
        asyncio.create_task(_store_and_push(session_id, res_block, queue))

    # dummy callbacks for HTTP logging (we ignore)
    def api_resp_cb(request, response, error): ...

    await sampling_loop(
        model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514"),
        provider=APIProvider.ANTHROPIC,
        system_prompt_suffix="",
        messages=messages,
        output_callback=output_cb,
        tool_output_callback=tool_output_cb,
        api_response_callback=api_resp_cb,
        api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        tool_version="computer_use_20250124",
        max_tokens=4096,
    )


async def _store_and_push(session_id: str, block: BetaContentBlockParam,
                          queue: asyncio.Queue):
    """Persist the block (flatten to text or save image) then push SSE."""
    async with async_session() as db:
        if block["type"] == "text":
            db.add(DBMessage(session_id=session_id,
                             role="assistant",
                             content=block["text"]))
        elif block["type"] == "image":
            # save PNG to disk, store path; real prod code would S3 or BLOB
            data = base64.b64decode(block["source"]["data"])
            fname = f"{session_id}_{datetime.utcnow().timestamp()}.png"
            path = MEDIA_ROOT / fname
            path.write_bytes(data)
            db.add(DBMessage(session_id=session_id,
                             role="assistant",
                             content=f"[image] {path}"))
        elif block["type"] in ("tool_use", "tool_result", "thinking"):
            # store as JSON string
            import json, uuid
            db.add(DBMessage(session_id=session_id,
                             role="assistant",
                             content=f"[{block['type']}] {uuid.uuid4().hex} :: {json.dumps(_serialize_block(block))}"))
        await db.commit()

    # push to live clients
    await queue.put(Message(role="assistant", content=str(block)))
