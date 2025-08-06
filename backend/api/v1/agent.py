# app/api/v1/agent.py

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session, select
from uuid import UUID
import asyncio

from computer_use_demo import sampling_loop, APIProvider
from backend.api.v1.stream import publish_task_event
from backend.db import get_session, Task, Message, Event, Screenshot
from backend.utils import save_screenshot_and_return_url, compute_sha256

router = APIRouter(prefix="/tasks", tags=["Agent"])


@router.post("/{task_id}/message", status_code=204)
def post_user_message(
    task_id: UUID,
    message: dict,  # assume { "text": "hello" } or Claude block format
    session: Session = Depends(get_session),
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")

    last_ordering = session.exec(
        select(Message.ordering).where(Message.task_id == task_id).order_by(Message.ordering.desc())
    ).first() or 0

    msg = Message(
        task_id=task_id,
        role="user",
        content=message,
        ordering=last_ordering + 1,
    )
    session.add(msg)
    session.commit()

    publish_task_event(str(task_id), {
        "type": "message",
        "role": "user",
        "content": message,
        "ordering": msg.ordering,
    })


@router.post("/{task_id}/start", status_code=202)
def start_task(
    task_id: UUID,
    bg: BackgroundTasks,
    session: Session = Depends(get_session),
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")

    # Launch the agent loop as a background task
    bg.add_task(run_agent_loop, str(task_id))
    return {"detail": "Task started"}


async def run_agent_loop(task_id: str):
    # Create a fresh DB session (cannot reuse the request-scoped one)
    from backend.db import SessionLocal
    session = SessionLocal()

    # 1) Load any prior messages and convert them for Claude's input
    raw = session.exec(select(Message).where(Message.task_id == task_id).order_by(Message.ordering)).all()
    messages = [{"role": m.role, "content": m.content} for m in raw]

    # Start ordering where we left off
    ordering = max((m["ordering"] for m in raw), default=0) + 1

    def output_callback(block):
        nonlocal ordering
        # Store the assistant message in DB
        msg = Message(
            task_id=UUID(task_id),
            role="assistant",
            content=block if isinstance(block, dict) else {"text": block},
            ordering=ordering,
        )
        session.add(msg)
        session.commit()

        # Broadcast over stream
        publish_task_event(task_id, {
            "type": "message",
            "role": msg.role,
            "content": msg.content,
            "ordering": msg.ordering,
        })
        ordering += 1

    async def tool_output_callback(tool_result, tool_use_id):
        nonlocal ordering

        # 1. Save screenshot if exists
        if tool_result.base64_image:
            url = save_screenshot_and_return_url(tool_result.base64_image)
            sha = compute_sha256(tool_result.base64_image)

            screenshot = Screenshot(
                event_id=None,  # optionally tie to event_id after inserting event
                url=url,
                sha256=sha,
            )
            session.add(screenshot)
            session.commit()

            publish_task_event(task_id, {
                "type": "screenshot",
                "url": screenshot.url,
                "sha256": screenshot.sha256,
                "ordering": ordering,
            })
            ordering += 1

        # 2. Save as Event
        event = Event(
            task_id=UUID(task_id),
            kind=tool_result.name or "tool_use",
            ordering=ordering,
            payload={
                "input": tool_result.input,
                "output": tool_result.output,
                "tool_use_id": tool_use_id,
            },
        )
        session.add(event)
        session.commit()

        publish_task_event(task_id, {
            "type": "event",
            "kind": event.kind,
            "payload": event.payload,
            "ordering": event.ordering,
        })
        ordering += 1

        # 3. Optional: Stream text output if exists
        if tool_result.output:
            publish_task_event(task_id, {
                "type": "tool_result",
                "content": tool_result.output,
                "ordering": ordering,
            })
            ordering += 1

    def api_response_callback(request, response, error):
        # Optional: Log or store Claude’s raw responses
        pass

    # 3) Run the Claude agent loop
    await sampling_loop(
        model="claude-sonnet-4-20250514",
        provider=APIProvider.ANTHROPIC,
        system_prompt_suffix="",
        messages=messages,
        output_callback=output_callback,
        tool_output_callback=tool_output_callback,
        api_response_callback=api_response_callback,
        api_key="YOUR_API_KEY",
        tool_version="computer_use_20250124",
    )
