import React, { useRef } from 'react';
import { Upload } from 'lucide-react';

interface UploadDropzoneProps {
  onFileUpload?: (files: File[]) => void;
  disabled?: boolean;
}

export const UploadDropzone: React.FC<UploadDropzoneProps> = ({ 
  onFileUpload, 
  disabled = false 
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (files: FileList) => {
    if (onFileUpload && !disabled) {
      onFileUpload(Array.from(files));
    }
  };

  const handleClick = () => {
    if (!disabled) {
      fileInputRef.current?.click();
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFileSelect(e.target.files);
    }
  };

  return (
    <div
      onClick={handleClick}
      className={`border-2 border-dashed border-gray-300 rounded-lg p-6 text-center transition-colors ${
        disabled 
          ? 'opacity-50 cursor-not-allowed' 
          : 'hover:border-gray-400 cursor-pointer'
      }`}
    >
      <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
      <p className="text-sm text-gray-600">
        {disabled ? 'Select a task to upload files' : 'Drop files here or click to upload'}
      </p>
      <input
        ref={fileInputRef}
        type="file"
        multiple
        className="hidden"
        onChange={handleInputChange}
        disabled={disabled}
      />
    </div>
  );
};