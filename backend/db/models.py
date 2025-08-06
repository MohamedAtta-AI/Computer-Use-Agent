from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column
from uuid import UUID, uuid4
from datetime import datetime

class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str
    status: str = Field(default="active")
    created_at: datetime = Field(default_factory=datetime.now)

    messages: list["Message"] = Relationship(back_populates="task")
    events: list["Event"] = Relationship(back_populates="task")
    media: list["Media"] = Relationship(back_populates="task")


class Message(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    role: str
    content: dict = Field(sa_column=Column(JSONB))
    ordering: int
    created_at: datetime = Field(default_factory=datetime.now)

    task_id: UUID = Field(foreign_key="task.id")
    task: Task = Relationship(back_populates="messages")


class Event(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    kind: str
    ordering: int
    created_at: datetime = Field(default_factory=datetime.now)
    payload: dict = Field(sa_column=Column(JSONB))

    task_id: UUID = Field(foreign_key="task.id")
    task: Task = Relationship(back_populates="events")
    screenshots: list["Screenshot"] = Relationship(back_populates="event")


class Screenshot(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    url: str
    sha256: str

    event_id: UUID = Field(foreign_key="event.id")
    event: Event = Relationship(back_populates="screenshots")


class Media(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    uploaded_by: str
    filename: str
    content_type: str
    url: str
    sha256: str
    created_at: datetime = Field(default_factory=datetime.now)

    task_id: UUID = Field(foreign_key="task.id")
    task: Task = Relationship(back_populates="media")