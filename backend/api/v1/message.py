from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from uuid import UUID

from backend.db import get_session, Message
from backend.schemas import MessageCreate, MessageRead

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.post("/", response_model=MessageRead)
def create_message(data: MessageCreate, session: Session = Depends(get_session)):
    msg = Message(**data.dict())
    session.add(msg)
    session.commit()
    session.refresh(msg)
    return msg


@router.get("/by-task/{task_id}", response_model=list[MessageRead])
def list_messages(task_id: UUID, session: Session = Depends(get_session)):
    return session.exec(select(Message).where(Message.task_id == task_id)).all()


@router.get("/{message_id}", response_model=MessageRead)
def get_message(message_id: UUID, session: Session = Depends(get_session)):
    message = session.get(Message, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message


@router.delete("/{message_id}", status_code=204)
def delete_message(message_id: UUID, session: Session = Depends(get_session)):
    msg = session.get(Message, message_id)
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    session.delete(msg)
    session.commit()
