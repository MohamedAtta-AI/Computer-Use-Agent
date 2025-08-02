from __future__ import annotations
from pathlib import Path
import asyncio
from typing import List, Dict

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from .agent_runner import run_agent
from .schemas import Ack, Message, SessionCreateResponse
from .state import create_session, get_session_state
from .config import load_config

load_config()

app = FastAPI(title="Claude Computer-Use Backend", version="0.3")

static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")

# ───────────────────────────── routes ──────────────────────────────

@app.post("/sessions", response_model=SessionCreateResponse)
async def new_session() -> SessionCreateResponse:
    return SessionCreateResponse(session_id=create_session())


@app.get("/sessions", response_model=Dict[str, int])
async def list_sessions():
    """
    Return all session IDs and how many messages each contains.
    Small helper so the front-end can show existing chats.
    """
    from .state import _SESSIONS          # import here to avoid circulars
    return {sid: len(st.messages) for sid, st in _SESSIONS.items()}


@app.post("/sessions/{session_id}/messages", response_model=Ack)
async def add_message(
    session_id: str,
    msg: Message,
    bg: BackgroundTasks,
) -> Ack:
    state = get_session_state(session_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Session not found")

    # 1️⃣ save + broadcast the user message immediately
    state.messages.append(msg)
    await state.queue.put(msg)

    # 2️⃣ schedule the assistant reply
    bg.add_task(run_agent, session_id)
    return Ack()


@app.get("/sessions/{session_id}/stream")
async def stream(session_id: str):
    state = get_session_state(session_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Session not found")

    async def event_gen():
        # backlog first
        for m in state.messages:
            yield f"data: {m.model_dump_json()}\n\n"
        # then live updates
        while True:
            m = await state.queue.get()
            yield f"data: {m.model_dump_json()}\n\n"

    return StreamingResponse(event_gen(), media_type="text/event-stream")


@app.get("/healthz")
async def health():
    return {"status": "ok"}
