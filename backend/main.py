import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .db.database import init_db
from backend.api.v1 import (
    task, message, event, screenshot, media, stream, agent
)

app = FastAPI()

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(task.router)
app.include_router(message.router)
app.include_router(event.router)
app.include_router(screenshot.router)
app.include_router(media.router)
app.include_router(stream.router)
app.include_router(agent.router)

@app.on_event("startup")
def on_startup():
    init_db()