from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlmodel import Session, select
from uuid import UUID, uuid4
from hashlib import sha256
import shutil
import os
from datetime import datetime

from backend.db import get_session, Media
from backend.schemas import MediaCreate, MediaRead

router = APIRouter(prefix="/media", tags=["Media"])


@router.post("/upload", response_model=MediaRead)
def upload_media_file(
    task_id: UUID = Form(...),
    uploaded_by: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    # Save file locally
    file_id = str(uuid4())
    ext = os.path.splitext(file.filename)[1]
    saved_path = f"uploads/{file_id}{ext}"

    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Compute SHA256
    with open(saved_path, "rb") as f:
        file_bytes = f.read()
        sha = sha256(file_bytes).hexdigest()

    # Build public URL
    url = f"/uploads/{file_id}{ext}"

    # Create DB entry
    media = Media(
        task_id=task_id,
        uploaded_by=uploaded_by,
        filename=file.filename,
        content_type=file.content_type,
        url=url,
        sha256=sha,
        created_at=datetime.utcnow(),
    )
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
