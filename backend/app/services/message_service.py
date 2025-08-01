"""
Service for managing messages in the database.
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import desc

from ..models import Message, MessageRole, MessageType
from ..schemas import MessageCreate


class MessageService:
    """Service for managing messages."""
    
    def __init__(self, db: DBSession):
        self.db = db
    
    def create_message(self, session_id: int, message_data: MessageCreate) -> Message:
        """Create a new message."""
        message = Message(
            session_id=session_id,
            role=message_data.role,
            message_type=message_data.message_type,
            content=message_data.content,
            message_metadata=message_data.metadata
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def create_user_message(self, session_id: int, content: str) -> Message:
        """Create a user message."""
        return self.create_message(
            session_id=session_id,
            message_data=MessageCreate(
                content=content,
                role=MessageRole.USER,
                message_type=MessageType.TEXT
            )
        )
    
    def create_assistant_message(self, session_id: int, content: str) -> Message:
        """Create an assistant message."""
        return self.create_message(
            session_id=session_id,
            message_data=MessageCreate(
                content=content,
                role=MessageRole.ASSISTANT,
                message_type=MessageType.TEXT
            )
        )
    
    def create_system_message(self, session_id: int, content: str) -> Message:
        """Create a system message."""
        return self.create_message(
            session_id=session_id,
            message_data=MessageCreate(
                content=content,
                role=MessageRole.SYSTEM,
                message_type=MessageType.TEXT
            )
        )
    
    def create_tool_message(
        self, 
        session_id: int, 
        content: str, 
        tool_name: str, 
        tool_result: dict = None
    ) -> Message:
        """Create a tool message."""
        metadata = {
            "tool_name": tool_name,
            "tool_result": tool_result or {}
        }
        return self.create_message(
            session_id=session_id,
            message_data=MessageCreate(
                content=content,
                role=MessageRole.TOOL,
                message_type=MessageType.TOOL_RESULT,
                metadata=metadata
            )
        )
    
    def get_messages(
        self, 
        session_id: int, 
        page: int = 1, 
        per_page: int = 50
    ) -> Tuple[List[Message], int]:
        """Get messages for a session with pagination."""
        query = self.db.query(Message).filter(Message.session_id == session_id)
        total = query.count()
        
        messages = query.order_by(desc(Message.created_at)).offset(
            (page - 1) * per_page
        ).limit(per_page).all()
        
        return messages, total
    
    def get_latest_message(self, session_id: int) -> Optional[Message]:
        """Get the latest message for a session."""
        return self.db.query(Message).filter(
            Message.session_id == session_id
        ).order_by(desc(Message.created_at)).first()
    
    def delete_message(self, message_id: int) -> bool:
        """Delete a message."""
        message = self.db.query(Message).filter(Message.id == message_id).first()
        if message:
            self.db.delete(message)
            self.db.commit()
            return True
        return False 