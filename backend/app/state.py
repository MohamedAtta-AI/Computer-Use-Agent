"""
In-memory queues only.

All durable data (sessions, messages) now lives in SQLite via
`backend/app/db.py`.  Each active session still needs an asyncio.Queue to
push real-time updates to any connected SSE clients, but these queues are
*not* persisted.
"""

import asyncio
from typing import Dict

# one queue per session id
_QUEUES: Dict[str, asyncio.Queue] = {}


def queue_for(session_id: str) -> asyncio.Queue:
    """
    Return the per-session asyncio.Queue, creating it if necessary.
    """
    return _QUEUES.setdefault(session_id, asyncio.Queue())
