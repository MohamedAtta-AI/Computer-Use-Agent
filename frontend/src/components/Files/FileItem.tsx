import React from 'react';
import { FileItem as FileItemType } from '../../types';
import { File, Folder } from 'lucide-react';

interface FileItemProps {
  file: FileItemType;
  onClick?: (file: FileItemType) => void;
}

export const FileItem: React.FC<FileItemProps> = ({ file, onClick }) => {
  const Icon = file.type === 'folder' ? Folder : File;

  return (
    <div
      onClick={() => onClick?.(file)}
      className="flex items-center space-x-3 p-2 hover:bg-gray-50 rounded-lg cursor-pointer transition-colors"
    >
      <Icon className={`w-4 h-4 ${
        file.type === 'folder' ? 'text-blue-500' : 'text-gray-500'
      }`} />
      <div className="flex-1 min-w-0">
        <p className="text-sm text-gray-900 truncate">{file.name}</p>
        <p className="text-xs text-gray-500">
          {file.size && `${file.size} • `}{file.timestamp}
        </p>
      </div>
    </div>
  );
};