from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from uuid import UUID

from backend.db import get_session, Media
from backend.schemas import MediaCreate, MediaRead

router = APIRouter(prefix="/media", tags=["Media"])


@router.post("/", response_model=MediaRead)
def upload_media(data: MediaCreate, session: Session = Depends(get_session)):
    media = Media(**data.dict())
    session.add(media)
    session.commit()
    session.refresh(media)
    return media


@router.get("/by-task/{task_id}", response_model=list[MediaRead])
def list_media(task_id: UUID, session: Session = Depends(get_session)):
    return session.exec(select(Media).where(Media.task_id == task_id)).all()


@router.get("/{media_id}", response_model=MediaRead)
def get_media(media_id: UUID, session: Session = Depends(get_session)):
    media = session.get(Media, media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    return media


@router.delete("/{media_id}", status_code=204)
def delete_media(media_id: UUID, session: Session = Depends(get_session)):
    media = session.get(Media, media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    session.delete(media)
    session.commit()
