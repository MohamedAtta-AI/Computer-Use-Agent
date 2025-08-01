"""
File service for managing file uploads
"""

import os
import uuid
import aiofiles
from typing import List, Optional
from sqlalchemy.orm import Session as DBSession
from fastapi import UploadFile

from ..config import settings
from ..models import File


class FileService:
    """Service for managing file uploads."""
    
    def __init__(self, db: DBSession):
        self.db = db
    
    async def upload_file(
        self, 
        session_id: int, 
        file: UploadFile
    ) -> File:
        """Upload a file for a session."""
        # Validate file size
        if file.size and file.size > settings.max_file_size:
            raise ValueError(f"File size {file.size} exceeds maximum allowed size {settings.max_file_size}")
        
        # Create upload directory if it doesn't exist
        os.makedirs(settings.upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(settings.upload_dir, unique_filename)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Create file record in database
        db_file = File(
            session_id=session_id,
            filename=unique_filename,
            original_filename=file.filename or "unknown",
            file_path=file_path,
            file_size=len(content),
            mime_type=file.content_type
        )
        
        self.db.add(db_file)
        self.db.commit()
        self.db.refresh(db_file)
        
        return db_file
    
    def get_file(self, file_id: int) -> Optional[File]:
        """Get a file by ID."""
        return self.db.query(File).filter(File.id == file_id).first()
    
    def get_files_by_session(self, session_id: int) -> List[File]:
        """Get all files for a session."""
        return self.db.query(File).filter(File.session_id == session_id).all()
    
    def delete_file(self, file_id: int) -> bool:
        """Delete a file."""
        file = self.get_file(file_id)
        if not file:
            return False
        
        # Delete physical file
        try:
            if os.path.exists(file.file_path):
                os.remove(file.file_path)
        except OSError:
            pass  # File might already be deleted
        
        # Delete database record
        self.db.delete(file)
        self.db.commit()
        return True
    
    def delete_files_by_session(self, session_id: int) -> int:
        """Delete all files for a session."""
        files = self.get_files_by_session(session_id)
        count = 0
        
        for file in files:
            # Delete physical file
            try:
                if os.path.exists(file.file_path):
                    os.remove(file.file_path)
            except OSError:
                pass
            
            count += 1
        
        # Delete database records
        deleted_count = self.db.query(File).filter(File.session_id == session_id).delete()
        self.db.commit()
        
        return deleted_count
    
    def get_file_path(self, file_id: int) -> Optional[str]:
        """Get the file path for a file ID."""
        file = self.get_file(file_id)
        return file.file_path if file else None
    
    def validate_file_type(self, filename: str) -> bool:
        """Validate if the file type is allowed."""
        allowed_extensions = {
            '.txt', '.pdf', '.doc', '.docx', '.xls', '.xlsx', 
            '.png', '.jpg', '.jpeg', '.gif', '.bmp',
            '.py', '.js', '.html', '.css', '.json', '.xml',
            '.csv', '.zip', '.tar', '.gz'
        }
        
        file_extension = os.path.splitext(filename)[1].lower()
        return file_extension in allowed_extensions 