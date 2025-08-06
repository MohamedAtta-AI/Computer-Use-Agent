from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from uuid import UUID

from backend.db import get_session, Event
from backend.schemas import EventCreate, EventRead

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/", response_model=EventRead)
def create_event(data: EventCreate, session: Session = Depends(get_session)):
    event = Event(**data.dict())
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@router.get("/by-task/{task_id}", response_model=list[EventRead])
def list_events(task_id: UUID, session: Session = Depends(get_session)):
    return session.exec(select(Event).where(Event.task_id == task_id)).all()


@router.get("/{event_id}", response_model=EventRead)
def get_event(event_id: UUID, session: Session = Depends(get_session)):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.delete("/{event_id}", status_code=204)
def delete_event(event_id: UUID, session: Session = Depends(get_session)):
    ev = session.get(Event, event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")
    session.delete(ev)
    session.commit()
