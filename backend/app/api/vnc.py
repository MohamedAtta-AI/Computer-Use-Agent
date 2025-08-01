"""
VNC API routes for virtual machine connection management
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from ..database import get_db
from ..schemas import VNCConnectionInfo, BaseResponse
from ..services.session_service import SessionService
from ..services.vnc_service import VNCService
from ..config import settings

router = APIRouter(prefix="/vnc", tags=["vnc"])


@router.get("/connection/{session_id}", response_model=VNCConnectionInfo)
async def get_vnc_connection(
    session_id: int,
    db: DBSession = Depends(get_db)
):
    """Get VNC connection information for a session."""
    session_service = SessionService(db)
    session = session_service.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Return VNC connection info
    return VNCConnectionInfo(
        host=session.vnc_host or settings.vnc_host,
        port=session.vnc_port or settings.vnc_port,
        password=session.vnc_password or settings.vnc_password,
        session_id=session_id
    )


@router.post("/connection/{session_id}", response_model=VNCConnectionInfo)
async def update_vnc_connection(
    session_id: int,
    vnc_info: VNCConnectionInfo,
    db: DBSession = Depends(get_db)
):
    """Update VNC connection information for a session."""
    session_service = SessionService(db)
    vnc_service = VNCService(db)
    
    session = session_service.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Create VNC connection
    connection_info = await vnc_service.create_session_connection(
        session_id=session_id,
        host=vnc_info.host,
        port=vnc_info.port,
        password=vnc_info.password
    )
    
    # Update session with VNC info
    from ..schemas import SessionUpdate
    session_update = SessionUpdate(
        vnc_host=vnc_info.host,
        vnc_port=vnc_info.port
    )
    
    updated_session = session_service.update_session(session_id, session_update)
    
    if not updated_session:
        raise HTTPException(status_code=500, detail="Failed to update VNC connection")
    
    return VNCConnectionInfo(
        host=updated_session.vnc_host or settings.vnc_host,
        port=updated_session.vnc_port or settings.vnc_port,
        password=updated_session.vnc_password or settings.vnc_password,
        session_id=session_id,
        is_connected=connection_info.get("is_connected", False),
        vnc_url=connection_info.get("vnc_url"),
        novnc_url=connection_info.get("novnc_url"),
        websocket_url=connection_info.get("websocket_url")
    )


@router.get("/status/{session_id}", response_model=BaseResponse)
async def get_vnc_status(
    session_id: int,
    db: DBSession = Depends(get_db)
):
    """Get VNC connection status for a session."""
    session_service = SessionService(db)
    session = session_service.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check if VNC is configured
    vnc_configured = bool(session.vnc_host and session.vnc_port)
    
    return BaseResponse(
        message="VNC connection status retrieved",
        data={
            "session_id": session_id,
            "vnc_configured": vnc_configured,
            "vnc_host": session.vnc_host,
            "vnc_port": session.vnc_port,
            "session_status": session.status
        }
    )


@router.post("/test/{session_id}", response_model=BaseResponse)
async def test_vnc_connection(
    session_id: int,
    db: DBSession = Depends(get_db)
):
    """Test VNC connection for a session."""
    session_service = SessionService(db)
    session = session_service.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get VNC connection info
    vnc_host = session.vnc_host or settings.vnc_host
    vnc_port = session.vnc_port or settings.vnc_port
    
    try:
        # Simple connection test (you might want to implement actual VNC connection testing)
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((vnc_host, vnc_port))
        sock.close()
        
        if result == 0:
            return BaseResponse(
                message="VNC connection test successful",
                data={
                    "session_id": session_id,
                    "vnc_host": vnc_host,
                    "vnc_port": vnc_port,
                    "connection_status": "success"
                }
            )
        else:
            return BaseResponse(
                message="VNC connection test failed",
                data={
                    "session_id": session_id,
                    "vnc_host": vnc_host,
                    "vnc_port": vnc_port,
                    "connection_status": "failed",
                    "error": f"Connection refused on {vnc_host}:{vnc_port}"
                }
            )
            
    except Exception as e:
                    return BaseResponse(
                message="VNC connection test failed",
                data={
                    "session_id": session_id,
                    "vnc_host": vnc_host,
                    "vnc_port": vnc_port,
                    "connection_status": "error",
                    "error": str(e)
                }
            )


@router.delete("/connection/{session_id}", response_model=BaseResponse)
async def delete_vnc_connection(
    session_id: int,
    db: DBSession = Depends(get_db)
):
    """Delete VNC connection for a session."""
    session_service = SessionService(db)
    vnc_service = VNCService(db)
    
    session = session_service.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Close VNC connection
    success = await vnc_service.close_session_connection(session_id)
    
    return BaseResponse(
        message="VNC connection closed" if success else "No VNC connection found",
        data={
            "session_id": session_id,
            "connection_closed": success
        }
    ) 