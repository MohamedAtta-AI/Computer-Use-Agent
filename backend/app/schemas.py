"""
Pydantic schemas for API request and response validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from .config import settings


class BaseResponse(BaseModel):
    """Base response model."""
    success: bool = True
    message: Optional[str] = None


# Session schemas
class SessionCreate(BaseModel):
    """Schema for creating a new session."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    model_name: str = Field(default=settings.anthropic_model)
    system_prompt: Optional[str] = None
    max_tokens: int = Field(default=settings.default_max_tokens, ge=1, le=128000)
    temperature: float = Field(default=settings.default_temperature, ge=0.0, le=2.0)


class SessionUpdate(BaseModel):
    """Schema for updating a session."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None


class SessionResponse(BaseModel):
    """Schema for session response."""
    id: int
    title: str
    description: Optional[str]
    status: str
    user_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    model_name: str
    system_prompt: Optional[str]
    max_tokens: int
    temperature: float
    vnc_host: Optional[str]
    vnc_port: Optional[int]
    
    class Config:
        from_attributes = True


class SessionListResponse(BaseResponse):
    """Schema for session list response."""
    sessions: List[SessionResponse]
    total: int
    page: int
    per_page: int


# Message schemas
class MessageCreate(BaseModel):
    """Schema for creating a new message."""
    content: str = Field(..., min_length=1)
    role: str = Field(..., pattern="^(user|assistant|system|tool)$")
    message_type: str = Field(default="text", pattern="^(text|tool_call|tool_result|image|file)$")
    metadata: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    """Schema for message response."""
    id: int
    session_id: int
    role: str
    message_type: str
    content: str
    message_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True


class MessageListResponse(BaseResponse):
    """Schema for message list response."""
    messages: List[MessageResponse]
    total: int
    page: int
    per_page: int


# File schemas
class FileUploadResponse(BaseModel):
    """Schema for file upload response."""
    id: int
    session_id: int
    filename: str
    original_filename: str
    file_size: int
    mime_type: Optional[str]
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


class FileListResponse(BaseResponse):
    """Schema for file list response."""
    files: List[FileUploadResponse]
    total: int


# Agent task schemas
class AgentTaskCreate(BaseModel):
    """Schema for creating an agent task."""
    task_type: str = Field(..., min_length=1)
    input_data: Optional[Dict[str, Any]] = None


class AgentTaskResponse(BaseModel):
    """Schema for agent task response."""
    id: int
    session_id: int
    task_type: str
    status: str
    input_data: Optional[Dict[str, Any]]
    output_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Chat schemas
class ChatMessage(BaseModel):
    """Schema for chat message."""
    role: str
    content: str
    message_type: str = "text"
    metadata: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    """Schema for chat request."""
    message: str = Field(..., min_length=1)
    session_id: int


class ChatResponse(BaseModel):
    """Schema for chat response."""
    message_id: int
    content: str
    role: str
    message_type: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime


# VNC schemas
class VNCConnectionInfo(BaseModel):
    """Schema for VNC connection information."""
    host: str
    port: int
    password: Optional[str] = None
    session_id: int
    is_connected: Optional[bool] = None
    vnc_url: Optional[str] = None
    novnc_url: Optional[str] = None
    websocket_url: Optional[str] = None


# WebSocket schemas
class WebSocketMessage(BaseModel):
    """Schema for WebSocket messages."""
    type: str = Field(..., description="Message type: chat, tool_call, tool_result, status")
    data: Dict[str, Any]
    session_id: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Error schemas
class ErrorResponse(BaseModel):
    """Schema for error responses."""
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None 