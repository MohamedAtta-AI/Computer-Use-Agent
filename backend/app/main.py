from __future__ import annotations

from pathlib import Path
from typing import Dict, List
from uuid import uuid4

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, UploadFile, File, Form, APIRouter, WebSocket
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select, Column, String
from sqlalchemy.ext.asyncio import AsyncSession
import websockets

from .config import load_config
from .compute_runner import run_computer_use_session
from .db import Message as DBMessage, Session as DBSession, get_db, init_db, Base
from .schemas import Ack, Message, SessionCreateResponse
from .state import queue_for


UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

class DBFile(Base):  # add model + alembic later
    __tablename__ = "files"
    id = Column(String, primary_key=True)
    session_id = Column(String)
    name = Column(String)
    path = Column(String)


load_config()

app = FastAPI(title="Claude Computer-Use Backend", version="0.4")
api_router = APIRouter(prefix="/api")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

# after static mount – serve index.html for React router
@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    index = static_dir / "index.html"
    return FileResponse(index)


# ────────────── lifecycle ──────────────
@app.on_event("startup")
async def _startup():
    await init_db()


# ────────────── routes ──────────────
@api_router.post("/sessions", response_model=SessionCreateResponse)
async def new_session(db: AsyncSession = Depends(get_db)) -> SessionCreateResponse:
    sid = str(uuid4())
    db.add(DBSession(id=sid))
    await db.commit()
    return SessionCreateResponse(session_id=sid)


@api_router.get("/sessions", response_model=Dict[str, int])
async def list_sessions(db=Depends(get_db)):
    rows = await db.execute(
        select(DBSession.id, func.count(DBMessage.id))
        .join(DBMessage, DBMessage.session_id == DBSession.id, isouter=True)
        .group_by(DBSession.id)
    )
    return {row[0]: row[1] for row in rows.all()}


@api_router.post("/sessions/{session_id}/messages", response_model=Ack)
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
    bg.add_task(run_computer_use_session, session_id)
    return Ack()


@api_router.get("/sessions/{session_id}/stream")
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


@api_router.get("/healthz")
async def health():
    return {"status": "ok"}


@api_router.post("/files/upload", response_model=Ack)
async def upload_file(session_id: str = Form(...), f: UploadFile = File(...), db=Depends(get_db)):
    fid = str(uuid4())
    dest = UPLOAD_DIR / fid
    dest.write_bytes(await f.read())
    db.add(DBFile(id=fid, session_id=session_id, name=f.filename, path=str(dest)))
    await db.commit()
    return {"id": fid, "name": f.filename, "url": f"/files/{fid}"}

@api_router.get("/files/{fid}")
async def get_file(fid: str, db=Depends(get_db)):
    rec = await db.get(DBFile, fid)
    if not rec: raise HTTPException(404)
    return FileResponse(rec.path, filename=rec.name)

@api_router.get("/files")
async def list_files(session_id: str, db=Depends(get_db)):
    rows = await db.execute(select(DBFile).where(DBFile.session_id == session_id))
    return [dict(id=r.id, name=r.name, url=f"/files/{r.id}") for r in rows.scalars()]

@api_router.delete("/files/{fid}", response_model=Ack)
async def delete_file(fid: str, db=Depends(get_db)):
    rec = await db.get(DBFile, fid)
    if not rec: raise HTTPException(404)
    Path(rec.path).unlink(missing_ok=True)
    await db.delete(rec); await db.commit(); return Ack()

# ────────────── static test UI (already added) ──────────────
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")

@app.websocket("/api/vnc")
async def vnc_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        # Connect to noVNC WebSocket
        async with websockets.connect("ws://localhost:6080/websockify") as vnc_ws:
            # Bidirectional proxy
            async def forward_to_vnc():
                try:
                    while True:
                        data = await websocket.receive_bytes()
                        await vnc_ws.send(data)
                except:
                    pass

            async def forward_from_vnc():
                try:
                    while True:
                        data = await vnc_ws.recv()
                        if isinstance(data, bytes):
                            await websocket.send_bytes(data)
                        else:
                            await websocket.send_text(data)
                except:
                    pass

            # Run both directions concurrently
            await asyncio.gather(
                forward_to_vnc(),
                forward_from_vnc()
            )
    except Exception as e:
        print(f"VNC WebSocket error: {e}")
    finally:
        await websocket.close()

app.include_router(api_router)
