import { useState, useCallback } from 'react';
import { FileItem, BackendMedia } from '../types';
import { mediaAPI } from '../services/api';

export const useFiles = (taskId?: string) => {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Convert backend media to frontend file item
  const convertBackendMedia = (backendMedia: BackendMedia): FileItem => {
    return {
      id: backendMedia.id,
      name: backendMedia.filename,
      type: 'file',
      size: 'Unknown', // Backend doesn't store file size
      timestamp: new Date(backendMedia.created_at).toLocaleString(),
    };
  };

  // Upload file to backend
  const uploadFile = useCallback(async (file: File) => {
    if (!taskId) {
      setError('No task selected for file upload');
      return;
    }

    try {
      setUploading(true);
      setError(null);

      const backendMedia = await mediaAPI.upload(taskId, 'user', file);
      const fileItem = convertBackendMedia(backendMedia);
      
      setFiles(prev => [fileItem, ...prev]);
    } catch (err) {
      setError('Failed to upload file');
      console.error('Error uploading file:', err);
    } finally {
      setUploading(false);
    }
  }, [taskId]);

  // Add file to local state (for drag & drop)
  const addFile = useCallback((file: Omit<FileItem, 'id'>) => {
    const newFile = {
      ...file,
      id: Date.now().toString()
    };
    setFiles(prev => [newFile, ...prev]);
  }, []);

  // Handle file drop
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const droppedFiles = Array.from(e.dataTransfer.files);
    
    droppedFiles.forEach(file => {
      uploadFile(file);
    });
  }, [uploadFile]);

  // Handle drag over
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
  }, []);

  // Handle file upload via input
  const handleFileUpload = useCallback((uploadedFiles: File[]) => {
    uploadedFiles.forEach(file => {
      uploadFile(file);
    });
  }, [uploadFile]);

  return { 
    files, 
    addFile, 
    handleDrop, 
    handleDragOver, 
    handleFileUpload,
    uploading,
    error,
    uploadFile
  };
};