"""
Service for managing computer use agent interactions.
"""

import asyncio
import sys
import os
from typing import Any, Callable, Dict, List, Optional

from anthropic import Anthropic
from anthropic.types.beta import BetaMessageParam

from ..config import settings
from ..models import Session, SessionStatus
from ..core import sampling_loop, APIProvider, ToolVersion
from .session_service import SessionService
from .message_service import MessageService


class AgentService:
    """Service for managing computer use agent interactions."""
    
    def __init__(self, db):
        self.db = db
        self.session_service = SessionService(db)
        self.message_service = MessageService(db)
        self.anthropic_client = Anthropic(api_key=settings.anthropic_api_key)
        self.active_sessions: Dict[int, asyncio.Task] = {}
    
    async def process_user_message(
        self, 
        session_id: int, 
        user_message: str,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """Process a user message and generate a response."""
        # Get session
        session = self.session_service.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Update session status to running
        self.session_service.update_session_status(session_id, SessionStatus.RUNNING)
        
        # Create user message in database
        user_msg = self.message_service.create_user_message(session_id, user_message)
        
        try:
            # Get session messages for context
            messages, _ = self.message_service.get_messages(session_id, per_page=100)
            
            # Convert to Anthropic message format
            anthropic_messages = self._convert_to_anthropic_messages(messages)
            
            # Determine tool version based on model
            tool_version = self._get_tool_version(session.model_name)
            
            # Create progress callback
            def progress_handler(content_block):
                if progress_callback:
                    progress_callback({
                        "type": "content_block",
                        "data": content_block
                    })
            
            def tool_output_handler(tool_result, tool_id):
                if progress_callback:
                    progress_callback({
                        "type": "tool_output",
                        "data": {
                            "tool_result": tool_result,
                            "tool_id": tool_id
                        }
                    })
                
                # Save tool result to database
                self.message_service.create_tool_message(
                    session_id=session_id,
                    content=str(tool_result),
                    tool_name=tool_id,
                    tool_result=tool_result.__dict__ if hasattr(tool_result, '__dict__') else {}
                )
            
            def api_response_handler(request, response, error):
                if progress_callback:
                    progress_callback({
                        "type": "api_response",
                        "data": {
                            "request": str(request),
                            "response": str(response) if response else None,
                            "error": str(error) if error else None
                        }
                    })
            
            # Run the sampling loop
            await sampling_loop(
                model=session.model_name,
                provider=APIProvider.ANTHROPIC,
                system_prompt_suffix=session.system_prompt or "",
                messages=anthropic_messages,
                output_callback=progress_handler,
                tool_output_callback=tool_output_handler,
                api_response_callback=api_response_handler,
                api_key=settings.anthropic_api_key,
                max_tokens=session.max_tokens,
                tool_version=tool_version
            )
            
            # Update session status to completed
            self.session_service.update_session_status(session_id, SessionStatus.COMPLETED)
            
            return {
                "success": True,
                "session_id": session_id,
                "message_id": user_msg.id
            }
            
        except Exception as e:
            # Update session status to failed
            self.session_service.update_session_status(session_id, SessionStatus.FAILED)
            
            # Create error message
            self.message_service.create_system_message(
                session_id=session_id,
                content=f"Error processing message: {str(e)}"
            )
            
            raise
    
    def _convert_to_anthropic_messages(self, messages) -> List[BetaMessageParam]:
        """Convert database messages to Anthropic API format."""
        anthropic_messages = []
        
        for msg in messages:
            if msg.role == "user":
                anthropic_messages.append({
                    "role": "user",
                    "content": msg.content
                })
            elif msg.role == "assistant":
                anthropic_messages.append({
                    "role": "assistant",
                    "content": msg.content
                })
            elif msg.role == "tool":
                # Convert tool messages to tool result format
                anthropic_messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": msg.message_metadata.get("tool_id", "unknown"),
                        "content": msg.content,
                        "is_error": msg.message_metadata.get("is_error", False)
                    }]
                })
        
        return anthropic_messages
    
    def _get_tool_version(self, model_name: str) -> ToolVersion:
        """Determine tool version based on model name."""
        if "2025" in model_name:
            return ToolVersion.COMPUTER_USE_20250124
        else:
            return ToolVersion.COMPUTER_USE_20241022
    
    async def cancel_session(self, session_id: int) -> bool:
        """Cancel an active session."""
        if session_id in self.active_sessions:
            task = self.active_sessions[session_id]
            task.cancel()
            del self.active_sessions[session_id]
            
            # Update session status
            self.session_service.update_session_status(session_id, SessionStatus.CANCELLED)
            return True
        return False
    
    def get_session_status(self, session_id: int) -> Optional[Dict[str, Any]]:
        """Get the status of a session."""
        session = self.session_service.get_session(session_id)
        if not session:
            return None
        
        return {
            "session_id": session_id,
            "status": session.status,
            "is_active": session_id in self.active_sessions,
            "created_at": session.created_at,
            "updated_at": session.updated_at
        } 