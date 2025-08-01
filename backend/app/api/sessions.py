"""
Sessions API routes
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session as DBSession

from ..database import get_db
from ..models import SessionStatus
from ..schemas import (
    SessionCreate, 
    SessionUpdate, 
    SessionResponse, 
    SessionListResponse,
    BaseResponse,
    ErrorResponse
)
from ..services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/", response_model=SessionResponse)
async def create_session(
    session_data: SessionCreate,
    db: DBSession = Depends(get_db)
):
    """Create a new session."""
    try:
        session_service = SessionService(db)
        session = session_service.create_session(session_data)
        return session
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=SessionListResponse)
async def get_sessions(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    db: DBSession = Depends(get_db)
):
    """Get paginated sessions."""
    try:
        session_service = SessionService(db)
        sessions, total = session_service.get_sessions(
            user_id=user_id,
            page=page,
            per_page=per_page
        )
        
        return SessionListResponse(
            sessions=sessions,
            total=total,
            page=page,
            per_page=per_page
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: int,
    db: DBSession = Depends(get_db)
):
    """Get a specific session."""
    session_service = SessionService(db)
    session = session_service.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: int,
    session_data: SessionUpdate,
    db: DBSession = Depends(get_db)
):
    """Update a session."""
    session_service = SessionService(db)
    session = session_service.update_session(session_id, session_data)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session


@router.delete("/{session_id}", response_model=BaseResponse)
async def delete_session(
    session_id: int,
    db: DBSession = Depends(get_db)
):
    """Delete a session."""
    session_service = SessionService(db)
    success = session_service.delete_session(session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return BaseResponse(message="Session deleted successfully")


@router.post("/{session_id}/start", response_model=SessionResponse)
async def start_session(
    session_id: int,
    db: DBSession = Depends(get_db)
):
    """Start a session."""
    session_service = SessionService(db)
    session = session_service.update_session_status(session_id, SessionStatus.RUNNING)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session


@router.post("/{session_id}/pause", response_model=SessionResponse)
async def pause_session(
    session_id: int,
    db: DBSession = Depends(get_db)
):
    """Pause a session."""
    session_service = SessionService(db)
    session = session_service.update_session_status(session_id, SessionStatus.PAUSED)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session


@router.post("/{session_id}/complete", response_model=SessionResponse)
async def complete_session(
    session_id: int,
    db: DBSession = Depends(get_db)
):
    """Complete a session."""
    session_service = SessionService(db)
    session = session_service.update_session_status(session_id, SessionStatus.COMPLETED)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session


@router.post("/{session_id}/cancel", response_model=SessionResponse)
async def cancel_session(
    session_id: int,
    db: DBSession = Depends(get_db)
):
    """Cancel a session."""
    session_service = SessionService(db)
    session = session_service.update_session_status(session_id, SessionStatus.CANCELLED)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session 