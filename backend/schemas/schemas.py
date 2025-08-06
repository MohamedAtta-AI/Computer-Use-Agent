from sqlmodel import SQLModel
from typing import Optional, Any
from uuid import UUID
from datetime import datetime


# ---------- Task ----------
class TaskCreate(SQLModel):
    title: str
    status: str = "active"


class TaskRead(TaskCreate):
    id: UUID
    created_at: datetime


class TaskUpdate(SQLModel):
    title: str | None
    status: str | None


# ---------- Message ----------
class MessageCreate(SQLModel):
    task_id: UUID
    role: str
    content: dict
    ordering: int


class MessageRead(MessageCreate):
    id: UUID
    created_at: datetime


# ---------- Event ----------
class EventCreate(SQLModel):
    task_id: UUID
    kind: str
    payload: dict
    ordering: int


class EventRead(EventCreate):
    id: UUID
    created_at: datetime


# ---------- Screenshot ----------
class ScreenshotCreate(SQLModel):
    event_id: UUID
    url: str
    sha256: str


class ScreenshotRead(ScreenshotCreate):
    id: UUID


# ---------- Media ----------
class MediaCreate(SQLModel):
    task_id: UUID
    uploaded_by: str
    filename: str
    content_type: str
    url: str
    sha256: str


class MediaRead(MediaCreate):
    id: UUID
    created_at: datetime
