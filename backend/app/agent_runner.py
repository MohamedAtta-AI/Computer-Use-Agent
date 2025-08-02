"""
Thin wrapper that calls the Anthropic SDK once per session and streams the
assistant’s reply back into the session’s queue.

Designed to be scheduled from FastAPI’s BackgroundTasks.
"""

from __future__ import annotations

import asyncio
import os
from typing import Dict, List

from anthropic import Anthropic, APIError

from .schemas import Message
from .state import get_session_state  # helper to access the global store

# Environment-configurable defaults
_MODEL_NAME   = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
_MAX_TOKENS   = int(os.getenv("CLAUDE_MAX_TOKENS", "1024"))
_SYSTEM_PROMPT = "You are a helpful assistant."

# One asyncio.Lock per session so we never run two agent calls concurrently
_LOCKS: Dict[str, asyncio.Lock] = {}


async def run_agent(session_id: str) -> None:
    """
    • Reads the full message history for `session_id`
    • Calls Anthropic once
    • Appends an assistant Message to the history
    • Pushes it onto the SSE queue so all live clients see it
    """
    state = get_session_state(session_id)
    if state is None:
        # Session was deleted while the task was pending
        return

    lock = _LOCKS.setdefault(session_id, asyncio.Lock())
    if lock.locked():                # another run is already in flight
        return

    async with lock:
        api_messages: List[dict] = [
            {"role": m.role, "content": m.content} for m in state.messages
        ]

        client = Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            max_retries=3,
        )

        try:
            response = await asyncio.to_thread(
                client.messages.create,
                model=_MODEL_NAME,
                system=_SYSTEM_PROMPT,
                messages=api_messages,
                max_tokens=_MAX_TOKENS,
                temperature=0.7,
            )
            text_out = "".join(
                block.text for block in response.content if block.type == "text"
            )
        except APIError as exc:
            text_out = f"[API error] {exc}"

        assistant_msg = Message(role="assistant", content=text_out)
        state.messages.append(assistant_msg)
        await state.queue.put(assistant_msg)
