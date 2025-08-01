"""
VNC service for managing virtual machine connections
Simplified approach that works with external VNC servers
"""

import asyncio
import socket
import platform
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session as DBSession

from ..config import settings


class VNCService:
    """Service for managing VNC connections to external servers."""
    
    def __init__(self, db: DBSession):
        self.db = db
        self.active_connections: Dict[int, Dict[str, Any]] = {}
    
    async def test_connection(self, host: str, port: int, timeout: int = 5) -> bool:
        """Test if a VNC server is reachable."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    async def get_vnc_url(self, host: str, port: int, password: Optional[str] = None) -> str:
        """Generate a VNC URL for direct VNC clients."""
        if password:
            return f"vnc://{host}:{port}?password={password}"
        else:
            return f"vnc://{host}:{port}"
    
    async def get_novnc_url(self, host: str, port: int) -> str:
        """Generate noVNC URL for web-based access."""
        # Use a public noVNC service or local noVNC if available
        return f"http://localhost:6080/vnc.html?host={host}&port={port}&autoconnect=1&resize=scale"
    
    async def create_session_connection(self, session_id: int, host: str = "localhost", port: int = 5900, password: Optional[str] = None) -> Dict[str, Any]:
        """Create a VNC connection for a session."""
        try:
            # Test if VNC server is reachable
            is_connected = await self.test_connection(host, port)
            
            connection_info = {
                "session_id": session_id,
                "host": host,
                "port": port,
                "password": password,
                "is_connected": is_connected,
                "vnc_url": await self.get_vnc_url(host, port, password),
                "novnc_url": await self.get_novnc_url(host, port),
                "websocket_url": f"ws://{host}:{port}",
                "connection_type": "vnc"
            }
            
            # Store connection info
            self.active_connections[session_id] = connection_info
            
            return connection_info
            
        except Exception as e:
            return {
                "session_id": session_id,
                "host": host,
                "port": port,
                "password": password,
                "is_connected": False,
                "error": str(e),
                "connection_type": "vnc"
            }
    
    async def get_session_connection(self, session_id: int) -> Optional[Dict[str, Any]]:
        """Get VNC connection info for a session."""
        return self.active_connections.get(session_id)
    
    async def close_session_connection(self, session_id: int) -> bool:
        """Close VNC connection for a session."""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            return True
        return False
    
    async def list_active_connections(self) -> Dict[int, Dict[str, Any]]:
        """List all active VNC connections."""
        return self.active_connections.copy() 