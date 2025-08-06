from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from uuid import UUID

from backend.db import get_session, Screenshot
from backend.schemas import ScreenshotCreate, ScreenshotRead

router = APIRouter(prefix="/screenshots", tags=["Screenshots"])


@router.post("/", response_model=ScreenshotRead)
def create_screenshot(data: ScreenshotCreate, session: Session = Depends(get_session)):
    sc = Screenshot(**data.dict())
    session.add(sc)
    session.commit()
    session.refresh(sc)
    return sc


@router.get("/by-event/{event_id}", response_model=list[ScreenshotRead])
def list_screenshots(event_id: UUID, session: Session = Depends(get_session)):
    return session.exec(select(Screenshot).where(Screenshot.event_id == event_id)).all()


@router.get("/{screenshot_id}", response_model=ScreenshotRead)
def get_screenshot(screenshot_id: UUID, session: Session = Depends(get_session)):
    sc = session.get(Screenshot, screenshot_id)
    if not sc:
        raise HTTPException(status_code=404, detail="Screenshot not found")
    return sc


@router.delete("/{screenshot_id}", status_code=204)
def delete_screenshot(screenshot_id: UUID, session: Session = Depends(get_session)):
    sc = session.get(Screenshot, screenshot_id)
    if not sc:
        raise HTTPException(status_code=404, detail="Screenshot not found")
    session.delete(sc)
    session.commit()
