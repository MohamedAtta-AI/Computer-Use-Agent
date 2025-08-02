from __future__ import annotations

import asyncio
import os
from typing import Dict, List

from anthropic import Anthropic, APIError
from sqlalchemy import select

from .db import Message as DBMessage, Session as DBSession, async_session
from .schemas import Message
from .state import queue_for

_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
_MAX_TOKENS = int(os.getenv("CLAUDE_MAX_TOKENS", "1024"))
_SYSTEM_PROMPT = "You are a helpful assistant."

_LOCKS: Dict[str, asyncio.Lock] = {}


async def run_agent(session_id: str) -> None:
    lock = _LOCKS.setdefault(session_id, asyncio.Lock())
    if lock.locked():  # another run already queued
        return

    async with lock, async_session() as db:
        # 1 collect full history from DB
        rows = await db.execute(
            select(DBMessage).where(DBMessage.session_id == session_id).order_by(DBMessage.id)
        )
        history = rows.scalars().all()
        api_messages: List[dict] = [
            {"role": m.role, "content": m.content} for m in history
        ]

        # 2 call Anthropic (in thread pool)
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""), max_retries=3)
        try:
            response = await asyncio.to_thread(
                client.messages.create,
                model=_MODEL,
                system=_SYSTEM_PROMPT,
                messages=api_messages,
                max_tokens=_MAX_TOKENS,
                temperature=0.7,
            )
            text_out = "".join(
                b.text for b in response.content if b.type == "text"
            )
        except APIError as exc:
            text_out = f"[API error] {exc}"

        # 3 persist + broadcast assistant reply
        msg_db = DBMessage(session_id=session_id, role="assistant", content=text_out)
        db.add(msg_db)
        await db.commit()

    assistant_msg = Message(role="assistant", content=text_out)
    await queue_for(session_id).put(assistant_msg)
