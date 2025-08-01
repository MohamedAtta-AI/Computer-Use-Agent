"""
Session service for managing agent sessions
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import desc

from ..models import Session, SessionStatus
from ..schemas import SessionCreate, SessionUpdate


class SessionService:
    """Service for managing agent sessions."""
    
    def __init__(self, db: DBSession):
        self.db = db
    
    def create_session(self, session_data: SessionCreate, user_id: Optional[str] = None) -> Session:
        """Create a new session."""
        session = Session(
            title=session_data.title,
            description=session_data.description,
            model_name=session_data.model_name,
            system_prompt=session_data.system_prompt,
            max_tokens=session_data.max_tokens,
            temperature=session_data.temperature,
            user_id=user_id,
            status=SessionStatus.CREATED
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def get_session(self, session_id: int) -> Optional[Session]:
        """Get a session by ID."""
        return self.db.query(Session).filter(Session.id == session_id).first()
    
    def get_sessions(
        self, 
        user_id: Optional[str] = None, 
        page: int = 1, 
        per_page: int = 20
    ) -> tuple[List[Session], int]:
        """Get paginated sessions."""
        query = self.db.query(Session)
        
        if user_id:
            query = query.filter(Session.user_id == user_id)
        
        total = query.count()
        sessions = query.order_by(desc(Session.updated_at)).offset(
            (page - 1) * per_page
        ).limit(per_page).all()
        
        return sessions, total
    
    def update_session(self, session_id: int, session_data: SessionUpdate) -> Optional[Session]:
        """Update a session."""
        session = self.get_session(session_id)
        if not session:
            return None
        
        update_data = session_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(session, field, value)
        
        session.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def update_session_status(self, session_id: int, status: SessionStatus) -> Optional[Session]:
        """Update session status."""
        session = self.get_session(session_id)
        if not session:
            return None
        
        session.status = status
        session.updated_at = datetime.utcnow()
        
        if status == SessionStatus.RUNNING and not session.started_at:
            session.started_at = datetime.utcnow()
        elif status in [SessionStatus.COMPLETED, SessionStatus.FAILED, SessionStatus.CANCELLED]:
            session.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def delete_session(self, session_id: int) -> bool:
        """Delete a session."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        self.db.delete(session)
        self.db.commit()
        return True
    
    def get_session_with_messages(self, session_id: int) -> Optional[Session]:
        """Get a session with its messages."""
        return self.db.query(Session).filter(Session.id == session_id).first() 