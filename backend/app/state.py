"""
Central place to keep the in-memory session store so we avoid circular imports.
"""

import asyncio
from typing import Dict, List, Optional

from .schemas import Message


class _SessionState:
    def __init__(self) -> None:
        self.messages: List[Message] = []
        self.queue: asyncio.Queue[Message] = asyncio.Queue()


_SESSIONS: Dict[str, _SessionState] = {}


def create_session() -> str:
    import uuid
    session_id = str(uuid.uuid4())
    _SESSIONS[session_id] = _SessionState()
    return session_id


def get_session_state(session_id: str) -> Optional[_SessionState]:
    return _SESSIONS.get(session_id)
