import React, { useState } from 'react';
import { UploadDropzone } from './UploadDropzone';
import { FileItem as FileItemType } from '../../types';
import { Upload } from 'lucide-react';

interface FileManagementProps {
  files: FileItemType[];
  onFileUpload?: (files: File[]) => void;
  onFileClick?: (file: FileItemType) => void;
  onDrop: (event: React.DragEvent<HTMLDivElement>) => void;
  onDragOver: (event: React.DragEvent<HTMLDivElement>) => void;
  uploading?: boolean;
  error?: string | null;
  selectedTaskId?: string | null;
}

export const FileManagement: React.FC<FileManagementProps> = ({
  files,
  onFileUpload,
  onFileClick,
  onDrop,
  onDragOver,
  uploading = false,
  error = null,
  selectedTaskId = null
}) => {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
    if (selectedTaskId) {
      onDrop(e);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (selectedTaskId) {
      setIsDragOver(true);
      onDragOver(e);
    }
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  return (
    <div className="flex flex-col">
      <div className="flex items-center space-x-2 p-2 border-b border-gray-200">
        <Upload className="w-4 h-4 text-gray-500" />
        <h3 className="text-sm font-medium text-gray-700">File Upload</h3>
        {selectedTaskId && (
          <span className="text-xs text-gray-500">Task: {selectedTaskId.slice(0, 8)}...</span>
        )}
      </div>
      
      {error && (
        <div className="p-2 bg-red-50 border-b border-red-200">
          <p className="text-xs text-red-600">{error}</p>
        </div>
      )}

      <div
        className={`p-2 ${isDragOver ? 'border-blue-400 bg-blue-50' : ''} ${!selectedTaskId ? 'opacity-50' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <UploadDropzone 
          onFileUpload={onFileUpload} 
          disabled={!selectedTaskId || uploading}
        />
      </div>
    </div>
  );
};