import React from 'react';
import { ChatSession } from '../Chat/ChatSession';
import { FileManagement } from '../Files/FileManagement';
import { ChatMessage, FileItem } from '../../types';

interface RightPanelProps {
  messages: ChatMessage[];
  files: FileItem[];
  inputValue: string;
  onInputChange: (value: string) => void;
  onSendMessage: (message: string) => void;
  onFileUpload?: (files: File[]) => void;
  onFileClick?: (file: FileItem) => void;
  onFileDrop: (event: React.DragEvent<HTMLDivElement>) => void;
  onFileDragOver: (event: React.DragEvent<HTMLDivElement>) => void;
  loading?: boolean;
  error?: string | null;
  uploading?: boolean;
  filesError?: string | null;
  selectedTaskId?: string | null;
}

export const RightPanel: React.FC<RightPanelProps> = ({
  messages,
  files,
  inputValue,
  onInputChange,
  onSendMessage,
  onFileUpload,
  onFileClick,
  onFileDrop,
  onFileDragOver,
  loading = false,
  error = null,
  uploading = false,
  filesError = null,
  selectedTaskId = null
}) => {
  return (
    <div className="w-96 bg-white border-l border-gray-200 flex flex-col h-screen">
      <ChatSession
        messages={messages}
        inputValue={inputValue}
        onInputChange={onInputChange}
        onSendMessage={onSendMessage}
        loading={loading}
        error={error}
        selectedTaskId={selectedTaskId}
      />
      <div className="border-t border-gray-200">
        <FileManagement
          files={files}
          onFileUpload={onFileUpload}
          onFileClick={onFileClick}
          onDrop={onFileDrop}
          onDragOver={onFileDragOver}
          uploading={uploading}
          error={filesError}
          selectedTaskId={selectedTaskId}
        />
      </div>
    </div>
  );
};