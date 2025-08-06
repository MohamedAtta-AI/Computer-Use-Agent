from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio
from uuid import UUID

router = APIRouter()

# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.task_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        
        # Remove from task connections
        for task_id, connections in self.task_connections.items():
            if client_id in [conn.client.host for conn in connections]:
                self.task_connections[task_id] = [
                    conn for conn in connections 
                    if conn.client.host != client_id
                ]

    async def subscribe_to_task(self, websocket: WebSocket, task_id: str):
        if task_id not in self.task_connections:
            self.task_connections[task_id] = []
        self.task_connections[task_id].append(websocket)

    async def send_personal_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(json.dumps(message))

    async def broadcast_to_task(self, message: dict, task_id: str):
        if task_id in self.task_connections:
            for connection in self.task_connections[task_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    # Remove dead connections
                    self.task_connections[task_id].remove(connection)

manager = ConnectionManager()

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "subscribe_task":
                await manager.subscribe_to_task(websocket, message["task_id"])
                await websocket.send_text(json.dumps({
                    "type": "subscribed",
                    "task_id": message["task_id"]
                }))
            
            elif message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(client_id)
