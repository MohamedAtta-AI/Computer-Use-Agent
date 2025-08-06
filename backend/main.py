from fastapi import FastAPI, Depends, HTTPException
from .db.database import init_db
from backend.api.v1 import task, message, event, screenshot, media

app = FastAPI()
app.include_router(task.router)
app.include_router(message.router)
app.include_router(event.router)
app.include_router(screenshot.router)
app.include_router(media.router)

@app.on_event("startup")
def on_startup():
    init_db()