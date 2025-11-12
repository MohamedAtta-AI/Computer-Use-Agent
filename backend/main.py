import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .db.database import init_db
from backend.api.v1 import (
    task, message, event, screenshot, media, stream, agent
)
from backend.api.websockets import router as websocket_router
from backend.core.config import get_settings

app = FastAPI()
settings = get_settings()

# CORS configuration for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(task.router)
app.include_router(message.router)
app.include_router(event.router)
app.include_router(screenshot.router)
app.include_router(media.router)
app.include_router(stream.router)
app.include_router(agent.router)
app.include_router(websocket_router)

@app.get("/")
def read_root():
    return {"message": "Computer Use Agent API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}

@app.on_event("startup")
def on_startup():
    init_db()