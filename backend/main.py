from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session
from .db.database import init_db, get_session
from .db.models import Task

app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


@app.post('/')
async def create_task(
    task: Task,
    session: Session = Depends(get_session)
):
    pass
