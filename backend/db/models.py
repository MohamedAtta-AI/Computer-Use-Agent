from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB
from uuid import UUID, uuid4
from datetime import datetime

class Message(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    task_id: UUID = Field(foreign_key="task.id")
    role: str
    content: str
    ordering: int
    created_at: datetime = Field(default_factory=datetime.now())

class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str
    status: str = Field(default="active")