# app/api/v1/agent.py

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session, select
from uuid import UUID
import asyncio
import os
import base64
from pydantic import BaseModel

from computer_use_demo import sampling_loop, APIProvider
from backend.api.v1.stream import publish_task_event
from backend.db import get_session, Task, Message, Event, Screenshot, Media
from backend.utils import save_screenshot_and_return_url, compute_sha256

router = APIRouter(prefix="/agent", tags=["Agent"])

# Global variable to track running tasks and their stop flags
running_tasks = {}

class MessageRequest(BaseModel):
    text: str

@router.post("/{task_id}/message", status_code=204)
def post_user_message(
    task_id: UUID,
    message: MessageRequest,
    bg: BackgroundTasks,
    session: Session = Depends(get_session),
):
    try:
        print(f"Received message for task {task_id}: {message}")
        
        task = session.get(Task, task_id)
        if not task:
            raise HTTPException(404, "Task not found")

        last_ordering = session.exec(
            select(Message.ordering).where(Message.task_id == task_id).order_by(Message.ordering.desc())
        ).first() or 0

        msg = Message(
            task_id=task_id,
            role="user",
            content={"text": message.text},
            ordering=last_ordering + 1,
        )
        session.add(msg)
        session.commit()

        print(f"Message saved with ordering {msg.ordering}")

        publish_task_event(str(task_id), {
            "type": "message",
            "role": "user",
            "content": {"text": message.text},
            "ordering": msg.ordering,
        })
        
        print(f"Task event published for task {task_id}")
        
        # Automatically start the agent loop to generate a response
        print(f"Starting agent loop for task {task_id}")
        bg.add_task(run_agent_loop, str(task_id))
        
    except Exception as e:
        print(f"Error in post_user_message: {e}")
        raise HTTPException(500, f"Internal server error: {str(e)}")


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


@router.post("/{task_id}/stop", status_code=202)
def stop_task(
    task_id: UUID,
    session: Session = Depends(get_session),
):
    task_id_str = str(task_id)
    print(f"Stop request received for task {task_id_str}")
    print(f"Currently running tasks: {list(running_tasks.keys())}")
    
    if task_id_str in running_tasks:
        # Set the stop flag
        running_tasks[task_id_str] = True
        print(f"Stop flag set for task {task_id_str}")
        
        # Publish stop event
        publish_task_event(task_id_str, {
            "type": "completion",
            "content": "Agent stopped by user",
            "ordering": 1,
        })
        print(f"Stop event published for task {task_id_str}")
        
        return {"detail": "Stop signal sent to task"}
    else:
        print(f"Task {task_id_str} not found in running tasks")
        raise HTTPException(404, "Task not running")


async def run_agent_loop(task_id: str):
    # Create a fresh DB session (cannot reuse the request-scoped one)
    from backend.db import SessionLocal
    from backend.core.config import get_settings
    
    session = SessionLocal()
    settings = get_settings()
    
    # Register this task as running
    running_tasks[task_id] = False
    print(f"Task {task_id} registered as running")
    
    try:
        print(f"Starting agent loop for task {task_id}")
        
        # Update task status to 'active' when agent starts
        task = session.get(Task, UUID(task_id))
        if task:
            task.status = 'active'
            session.add(task)
            session.commit()
            print(f"Task {task_id} status updated to 'active'")
        
        # 1) Load any prior messages and convert them for Claude's input
        raw = session.exec(select(Message).where(Message.task_id == task_id).order_by(Message.ordering)).all()
        
        # 2) Load media files for this task
        media_files = session.exec(select(Media).where(Media.task_id == task_id).order_by(Media.created_at)).all()
        
        # Helper function to process media files into content blocks
        def process_media_files(media_list):
            """Convert media files to Claude API content blocks."""
            content_blocks = []
            file_references = []
            
            for media in media_list:
                file_path = media.url.lstrip('/')  # Remove leading slash: /uploads/file -> uploads/file
                
                if not os.path.exists(file_path):
                    print(f"Warning: Media file not found at {file_path}")
                    continue
                
                # Determine file type from content_type or extension
                content_type = media.content_type or ""
                is_image = content_type.startswith("image/")
                is_text = (
                    content_type.startswith("text/") or
                    content_type in ["application/json", "application/xml"] or
                    media.filename.endswith(('.txt', '.md', '.py', '.js', '.json', '.xml', '.csv', '.log'))
                )
                
                try:
                    if is_image:
                        # Convert image to base64
                        with open(file_path, "rb") as f:
                            image_data = f.read()
                            base64_data = base64.b64encode(image_data).decode('utf-8')
                            
                            # Determine media type
                            if content_type.startswith("image/"):
                                media_type = content_type
                            elif media.filename.endswith('.png'):
                                media_type = "image/png"
                            elif media.filename.endswith(('.jpg', '.jpeg')):
                                media_type = "image/jpeg"
                            elif media.filename.endswith('.gif'):
                                media_type = "image/gif"
                            elif media.filename.endswith('.webp'):
                                media_type = "image/webp"
                            else:
                                media_type = "image/png"  # Default
                            
                            content_blocks.append({
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": base64_data
                                }
                            })
                            file_references.append(f"Image: {media.filename}")
                            print(f"Added image file to context: {media.filename}")
                    
                    elif is_text:
                        # Read text file content
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            text_content = f.read()
                        
                        content_blocks.append({
                            "type": "text",
                            "text": f"File: {media.filename}\n\n{text_content}"
                        })
                        file_references.append(f"Text file: {media.filename}")
                        print(f"Added text file to context: {media.filename}")
                    
                    else:
                        # For other file types, just reference them
                        file_references.append(f"File: {media.filename} (type: {content_type})")
                        print(f"Referenced file (not included in context): {media.filename}")
                
                except Exception as e:
                    print(f"Error processing media file {media.filename}: {e}")
                    file_references.append(f"File: {media.filename} (error loading)")
            
            return content_blocks, file_references
        
        # Process media files
        media_content_blocks, file_references = process_media_files(media_files)
        
        # Convert database format to API format
        messages = []
        first_user_message_processed = False
        
        # Add regular messages, merging files with first user message if available
        for m in raw:
            # Convert our database format to API format
            if isinstance(m.content, dict) and "text" in m.content:
                # Our format: {"text": "message"}
                content = m.content["text"]
            elif isinstance(m.content, str):
                # Already a string
                content = m.content
            else:
                # Fallback: stringify the content
                content = str(m.content)
            
            # If this is the first user message and we have files, merge them
            if m.role == "user" and not first_user_message_processed and media_content_blocks:
                first_user_message_processed = True
                # Merge files with the first user message
                file_intro_text = "The following files have been uploaded for this task:\n" + "\n".join(f"- {ref}" for ref in file_references)
                
                # Create multi-modal content: intro + files + original message
                merged_content = [{"type": "text", "text": file_intro_text}]
                merged_content.extend(media_content_blocks)
                
                # Add the original user message text
                if isinstance(content, str):
                    merged_content.append({"type": "text", "text": content})
                else:
                    merged_content.append({"type": "text", "text": str(content)})
                
                messages.append({
                    "role": m.role,
                    "content": merged_content
                })
                print(f"Merged {len(media_content_blocks)} file content blocks with first user message")
            else:
                # Regular message
                messages.append({
                    "role": m.role,
                    "content": content
                })
        
        # If we have files but no user messages yet, add files as a separate message
        if media_content_blocks and not first_user_message_processed:
            file_intro_text = "The following files have been uploaded for this task:\n" + "\n".join(f"- {ref}" for ref in file_references)
            
            # Combine file intro with file content
            file_message_content = [{"type": "text", "text": file_intro_text}]
            file_message_content.extend(media_content_blocks)
            
            messages.append({
                "role": "user",
                "content": file_message_content
            })
            print(f"Added {len(media_content_blocks)} file content blocks as initial message")

        # Start ordering where we left off
        ordering = max((m.ordering for m in raw), default=0) + 1

        def output_callback(block):
            nonlocal ordering
            try:
                # Check if task should be stopped
                if running_tasks.get(task_id, False):
                    print(f"Task {task_id} stop flag detected, stopping output")
                    return
                
                # Handle different block types
                if isinstance(block, dict):
                    block_type = block.get("type")
                    
                    # Handle tool_use blocks - send as special event
                    if block_type == "tool_use":
                        # Store the tool_use block as-is in the message
                        msg = Message(
                            task_id=UUID(task_id),
                            role="assistant",
                            content=block,  # Store the full tool_use object
                            ordering=ordering,
                        )
                        session.add(msg)
                        session.commit()

                        # Broadcast tool_use as a special message type
                        publish_task_event(task_id, {
                            "type": "message",
                            "role": "assistant",
                            "content": block,  # Send the full tool_use object
                            "ordering": msg.ordering,
                        })
                        ordering += 1
                        print(f"Tool use block saved with ordering {msg.ordering}: {block.get('name', 'unknown')}")
                        return
                    
                    # Handle text blocks
                    elif block_type == "text":
                        text_content = block.get("text", "")
                    else:
                        # For other block types, stringify the content
                        text_content = str(block)
                else:
                    text_content = str(block)
                
                # Store the assistant message in DB with our format
                msg = Message(
                    task_id=UUID(task_id),
                    role="assistant",
                    content={"text": text_content},
                    ordering=ordering,
                )
                session.add(msg)
                session.commit()

                # Broadcast over stream with our format
                publish_task_event(task_id, {
                    "type": "message",
                    "role": msg.role,
                    "content": {"text": text_content},
                    "ordering": msg.ordering,
                })
                ordering += 1
                print(f"Assistant message saved with ordering {msg.ordering}: {text_content}")
            except Exception as e:
                print(f"Error in output_callback: {e}")

        async def tool_output_callback(tool_result, tool_use_id):
            nonlocal ordering
            try:
                # Check if task should be stopped
                if running_tasks.get(task_id, False):
                    print(f"Task {task_id} stop flag detected, stopping tool execution")
                    return
                
                # Update task status to 'running' when computer tools are used
                task = session.get(Task, UUID(task_id))
                if task and task.status != 'running':
                    task.status = 'running'
                    session.add(task)
                    session.commit()
                    print(f"Task {task_id} status updated to 'running' (computer tools used)")
                
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
            except Exception as e:
                print(f"Error in tool_output_callback: {e}")

        def api_response_callback(request, response, error):
            # Optional: Log or store Claude's raw responses
            if error:
                print(f"API response error: {error}")

        # 3) Run the Claude agent loop
        print(f"Running sampling loop with {len(messages)} messages")
        print(f"Message format: {messages}")
        
        # Check if task should be stopped before starting
        if running_tasks.get(task_id, False):
            print(f"Task {task_id} stop flag detected before starting, stopping")
            return
            
        await sampling_loop(
            model="claude-sonnet-4-20250514",
            provider=APIProvider.ANTHROPIC,
            system_prompt_suffix="",
            messages=messages,
            output_callback=output_callback,
            tool_output_callback=tool_output_callback,
            api_response_callback=api_response_callback,
            api_key=settings.anthropic_api_key,
            tool_version="computer_use_20250124",
        )
        
        # Check if task should be stopped after completion
        if running_tasks.get(task_id, False):
            print(f"Task {task_id} stop flag detected after completion, stopping")
            return
            
        print(f"Agent loop completed for task {task_id}")
        
        # Update task status to 'completed' when agent finishes
        task = session.get(Task, UUID(task_id))
        if task:
            task.status = 'completed'
            session.add(task)
            session.commit()
            print(f"Task {task_id} status updated to 'completed'")
        
        # Publish completion event
        publish_task_event(task_id, {
            "type": "completion",
            "content": "Agent completed successfully",
            "ordering": ordering if 'ordering' in locals() else 1,
        })
        print(f"Completion event published for task {task_id}")
        
    except Exception as e:
        print(f"Error in run_agent_loop for task {task_id}: {e}")
        # Update task status to 'failed' on error
        task = session.get(Task, UUID(task_id))
        if task:
            task.status = 'failed'
            session.add(task)
            session.commit()
            print(f"Task {task_id} status updated to 'failed'")
        
        # Publish error event
        publish_task_event(task_id, {
            "type": "error",
            "content": f"Agent error: {str(e)}",
            "ordering": ordering if 'ordering' in locals() else 1,
        })
    finally:
        # Clean up: remove task from running tasks
        if task_id in running_tasks:
            del running_tasks[task_id]
            print(f"Task {task_id} removed from running tasks")
        session.close()
