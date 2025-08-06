from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import asyncio
import json
from typing import AsyncGenerator

router = APIRouter(prefix="/tasks", tags=["Streaming"])

# In-memory task update queue
task_streams: dict[str, asyncio.Queue] = {}

def publish_task_event(task_id: str, event: dict):
    if task_id in task_streams:
        task_streams[task_id].put_nowait(event)

async def event_stream(task_id: str) -> AsyncGenerator[str, None]:
    queue = asyncio.Queue()
    task_streams[task_id] = queue

    try:
        while True:
            event = await queue.get()
            yield f"data: {json.dumps(event)}\n\n"
    except asyncio.CancelledError:
        print(f"[SSE] Closed stream for task {task_id}")
    finally:
        del task_streams[task_id]

@router.get("/{task_id}/stream")
async def stream_task_updates(task_id: str, request: Request):
    return StreamingResponse(event_stream(task_id), media_type="text/event-stream")
