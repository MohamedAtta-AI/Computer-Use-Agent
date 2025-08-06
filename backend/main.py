from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session
from .db.database import init_db, get_session
from .db.models import Task
from backend.api.v1 import task

app = FastAPI()
app.include_router(task.router)

@app.on_event("startup")
def on_startup():
    init_db()


@app.post('/')
async def create_task(
    task: Task,
    session: Session = Depends(get_session)
):
    pass
