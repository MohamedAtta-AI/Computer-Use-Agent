from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Dict, List
from uuid import uuid4

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import load_config
from .agent_runner import run_agent
from .db import Message as DBMessage, Session as DBSession, get_db, init_db
from .schemas import Ack, Message, SessionCreateResponse
from .state import queue_for

load_config()

app = FastAPI(title="Claude Computer-Use Backend", version="0.4")


# ────────────── lifecycle ──────────────
@app.on_event("startup")
async def _startup():
    await init_db()


# ────────────── routes ──────────────
@app.post("/sessions", response_model=SessionCreateResponse)
async def new_session(db: AsyncSession = Depends(get_db)) -> SessionCreateResponse:
    sid = str(uuid4())
    db.add(DBSession(id=sid))
    await db.commit()
    return SessionCreateResponse(session_id=sid)


@app.get("/sessions", response_model=Dict[str, int])
async def list_sessions(db=Depends(get_db)):
    rows = await db.execute(
        select(DBSession.id, func.count(DBMessage.id))
        .join(DBMessage, DBMessage.session_id == DBSession.id, isouter=True)
        .group_by(DBSession.id)
    )
    return {row[0]: row[1] for row in rows.all()}


@app.post("/sessions/{session_id}/messages", response_model=Ack)
async def add_message(
    session_id: str,
    msg: Message,
    bg: BackgroundTasks,
    db=Depends(get_db),
) -> Ack:
    # ensure session exists
    if not await db.get(DBSession, session_id):
        raise HTTPException(status_code=404, detail="Session not found")

    db.add(DBMessage(session_id=session_id, role=msg.role, content=msg.content))
    await db.commit()

    await queue_for(session_id).put(msg)
    bg.add_task(run_agent, session_id)
    return Ack()


@app.get("/sessions/{session_id}/stream")
async def stream(session_id: str, db=Depends(get_db)):
    if not await db.get(DBSession, session_id):
        raise HTTPException(status_code=404, detail="Session not found")

    # backlog first
    rows = await db.execute(
        select(DBMessage).where(DBMessage.session_id == session_id).order_by(DBMessage.id)
    )
    backlog = rows.scalars().all()

    queue = queue_for(session_id)

    async def event_gen():
        for m in backlog:
            yield f"data: {Message(role=m.role, content=m.content).json()}\n\n"
        while True:
            m: Message = await queue.get()
            yield f"data: {m.json()}\n\n"

    return StreamingResponse(event_gen(), media_type="text/event-stream")


@app.get("/healthz")
async def health():
    return {"status": "ok"}


# ────────────── static test UI (already added) ──────────────
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")
