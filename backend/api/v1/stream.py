from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import asyncio
import json
from typing import AsyncGenerator
from backend.api.websockets import manager

router = APIRouter(prefix="/tasks", tags=["Streaming"])

# In-memory task update queue
task_streams: dict[str, asyncio.Queue] = {}

def publish_task_event(task_id: str, event: dict):
    print(f"Publishing event for task {task_id}: {event}")
    try:
        if task_id in task_streams:
            task_streams[task_id].put_nowait(event)
            print(f"Event queued for SSE stream: {event}")
        else:
            print(f"No SSE stream found for task {task_id}")
        
        # Also broadcast via WebSocket
        asyncio.create_task(manager.broadcast_to_task(event, task_id))
        print(f"Event broadcasted via WebSocket: {event}")
    except Exception as e:
        print(f"Error publishing task event: {e}")
        # Don't let WebSocket errors break the main request

async def event_stream(task_id: str) -> AsyncGenerator[str, None]:
    print(f"[SSE] Starting stream for task {task_id}")
    queue = asyncio.Queue()
    task_streams[task_id] = queue
    print(f"[SSE] Stream registered for task {task_id}")

    try:
        while True:
            event = await queue.get()
            event_data = f"data: {json.dumps(event)}\n\n"
            print(f"[SSE] Sending event to task {task_id}: {event}")
            yield event_data
    except asyncio.CancelledError:
        print(f"[SSE] Closed stream for task {task_id}")
    finally:
        if task_id in task_streams:
            del task_streams[task_id]
        print(f"[SSE] Stream cleanup for task {task_id}")

@router.get("/{task_id}/stream")
async def stream_task_updates(task_id: str, request: Request):
    return StreamingResponse(event_stream(task_id), media_type="text/event-stream")
