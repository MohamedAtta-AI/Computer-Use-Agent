"""
Database models for the Computer Use Agent Backend.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class SessionStatus(str, Enum):
    """Session status enumeration."""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MessageRole(str, Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class MessageType(str, Enum):
    """Message type enumeration."""
    TEXT = "text"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    IMAGE = "image"
    FILE = "file"


class Session(Base):
    """Session model for managing agent tasks."""
    
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), default=SessionStatus.CREATED, nullable=False)
    user_id = Column(String(255), nullable=True, index=True)  # For future user management
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Agent configuration
    model_name = Column(String(100), nullable=False)
    system_prompt = Column(Text, nullable=True)
    max_tokens = Column(Integer, default=4096)
    temperature = Column(Integer, default=1)
    
    # VNC connection info
    vnc_host = Column(String(255), nullable=True)
    vnc_port = Column(Integer, nullable=True)
    vnc_password = Column(String(255), nullable=True)
    
    # Relationships
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    files = relationship("File", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Session(id={self.id}, title='{self.title}', status='{self.status}')>"


class Message(Base):
    """Message model for chat history."""
    
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    role = Column(String(50), nullable=False)
    message_type = Column(String(50), default=MessageType.TEXT, nullable=False)
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON, nullable=True)  # For tool calls, results, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    session = relationship("Session", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(id={self.id}, session_id={self.session_id}, role='{self.role}')>"


class File(Base):
    """File model for uploaded files."""
    
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    session = relationship("Session", back_populates="files")
    
    def __repr__(self):
        return f"<File(id={self.id}, filename='{self.filename}', session_id={self.session_id}')>"


class AgentTask(Base):
    """Agent task model for tracking individual tasks within a session."""
    
    __tablename__ = "agent_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    task_type = Column(String(100), nullable=False)  # e.g., "bash", "computer", "edit"
    status = Column(String(50), default="pending", nullable=False)
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<AgentTask(id={self.id}, session_id={self.session_id}, task_type='{self.task_type}')>" 