"""
Chat API endpoints for the Computer Use Agent Backend.
"""

import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Session as DBSession, Message
from ..schemas import ChatRequest, ChatResponse, WebSocketMessage
from ..services.agent_service import AgentService
from ..services.message_service import MessageService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/send", response_model=ChatResponse)
async def send_message(
    chat_request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Send a message to a session."""
    agent_service = AgentService(db)
    message_service = MessageService(db)
    
    try:
        # Process the message
        result = await agent_service.process_user_message(
            session_id=chat_request.session_id,
            user_message=chat_request.message
        )
        
        # Get the latest assistant message
        latest_message = message_service.get_latest_message(chat_request.session_id)
        
        if not latest_message or latest_message.role != "assistant":
            raise HTTPException(status_code=500, detail="No assistant response generated")
        
        return ChatResponse(
            message_id=latest_message.id,
            content=latest_message.content,
            role=latest_message.role,
            message_type=latest_message.message_type,
            metadata=latest_message.message_metadata,
            created_at=latest_message.created_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/messages", response_model=List[ChatResponse])
async def get_messages(
    session_id: int,
    page: int = 1,
    per_page: int = 50,
    db: Session = Depends(get_db)
):
    """Get messages for a session."""
    message_service = MessageService(db)
    
    try:
        messages, total = message_service.get_messages(
            session_id=session_id,
            page=page,
            per_page=per_page
        )
        
        return [
            ChatResponse(
                message_id=msg.id,
                content=msg.content,
                role=msg.role,
                message_type=msg.message_type,
                metadata=msg.message_metadata,
                created_at=msg.created_at
            )
            for msg in messages
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: int):
    """WebSocket endpoint for real-time chat."""
    await websocket.accept()
    
    try:
        db = next(get_db())
        message_service = MessageService(db)
        agent_service = AgentService(db)
        
        # Send connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection",
            "data": {"message": "Connected to chat session", "session_id": session_id},
            "session_id": session_id
        }))
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "chat":
                user_message = message_data.get("data", {}).get("message", "")
                
                # Create user message in database
                user_msg = message_service.create_user_message(session_id, user_message)
                
                # Send confirmation
                await websocket.send_text(json.dumps({
                    "type": "message_received",
                    "data": {"message_id": user_msg.id, "content": user_message},
                    "session_id": session_id
                }))
                
                # Process message with progress callback
                async def progress_callback(progress_data):
                    await websocket.send_text(json.dumps({
                        "type": "progress",
                        "data": progress_data,
                        "session_id": session_id
                    }))
                
                try:
                    await agent_service.process_user_message(
                        session_id=session_id,
                        user_message=user_message,
                        progress_callback=progress_callback
                    )
                    
                    # Get latest assistant message
                    latest_message = message_service.get_latest_message(session_id)
                    
                    if latest_message and latest_message.role == "assistant":
                        await websocket.send_text(json.dumps({
                            "type": "assistant_message",
                            "data": {
                                "message_id": latest_message.id,
                                "content": latest_message.content,
                                "role": latest_message.role,
                                "message_type": latest_message.message_type,
                                "metadata": latest_message.message_metadata,
                                "created_at": latest_message.created_at.isoformat()
                            },
                            "session_id": session_id
                        }))
                    
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "data": {"error": str(e)},
                        "session_id": session_id
                    }))
            
            elif message_data.get("type") == "cancel":
                # Cancel the session
                await agent_service.cancel_session(session_id)
                await websocket.send_text(json.dumps({
                    "type": "cancelled",
                    "data": {"message": "Session cancelled"},
                    "session_id": session_id
                }))
                break
    
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        print(f"WebSocket error for session {session_id}: {e}")
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "data": {"error": str(e)},
                "session_id": session_id
            }))
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass  # WebSocket might already be closed 