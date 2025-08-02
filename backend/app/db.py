"""
Database layer (SQLite via SQLAlchemy async).

• Session …… top-level chat container
• Message …… every user / assistant / tool utterance

The helper functions are tiny; all heavier logic stays in main / runner.
"""

from __future__ import annotations

import os
from typing import AsyncGenerator, List

import sqlalchemy as sa
from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

# --------------------------------------------------------------------------- #
# engine / sessionmaker
# --------------------------------------------------------------------------- #

DATABASE_URL = os.getenv(
    "DATABASE_URL", "sqlite+aiosqlite:///./data.db"
)  # persisted in project root
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)

# --------------------------------------------------------------------------- #
# models
# --------------------------------------------------------------------------- #


class Base(DeclarativeBase):
    pass


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    messages: Mapped[List["Message"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sessions.id", ondelete="CASCADE")
    )
    role: Mapped[str] = mapped_column(String(16))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    session: Mapped["Session"] = relationship(back_populates="messages")


# --------------------------------------------------------------------------- #
# utilities
# --------------------------------------------------------------------------- #


async def init_db() -> None:
    """Create tables on startup (SQLite, so fine for dev)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session