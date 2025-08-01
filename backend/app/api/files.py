"""
Files API routes for file upload management
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile
from sqlalchemy.orm import Session as DBSession

from ..database import get_db
from ..schemas import (
    FileUploadResponse,
    FileListResponse,
    BaseResponse
)
from ..services.file_service import FileService

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload/{session_id}", response_model=FileUploadResponse)
async def upload_file(
    session_id: int,
    file: UploadFile = FastAPIFile(...),
    db: DBSession = Depends(get_db)
):
    """Upload a file for a session."""
    try:
        file_service = FileService(db)
        
        # Validate file type
        if not file_service.validate_file_type(file.filename or ""):
            raise HTTPException(
                status_code=400, 
                detail=f"File type not allowed: {file.filename}"
            )
        
        # Upload file
        uploaded_file = await file_service.upload_file(session_id, file)
        return uploaded_file
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}", response_model=FileListResponse)
async def get_session_files(
    session_id: int,
    db: DBSession = Depends(get_db)
):
    """Get all files for a session."""
    try:
        file_service = FileService(db)
        files = file_service.get_files_by_session(session_id)
        
        return FileListResponse(
            files=files,
            total=len(files)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/file/{file_id}", response_model=FileUploadResponse)
async def get_file(
    file_id: int,
    db: DBSession = Depends(get_db)
):
    """Get a specific file."""
    file_service = FileService(db)
    file = file_service.get_file(file_id)
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    return file


@router.delete("/file/{file_id}", response_model=BaseResponse)
async def delete_file(
    file_id: int,
    db: DBSession = Depends(get_db)
):
    """Delete a file."""
    file_service = FileService(db)
    success = file_service.delete_file(file_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="File not found")
    
    return BaseResponse(message="File deleted successfully")


@router.delete("/{session_id}", response_model=BaseResponse)
async def delete_session_files(
    session_id: int,
    db: DBSession = Depends(get_db)
):
    """Delete all files for a session."""
    try:
        file_service = FileService(db)
        deleted_count = file_service.delete_files_by_session(session_id)
        
        return BaseResponse(
            message=f"Deleted {deleted_count} files from session {session_id}"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 