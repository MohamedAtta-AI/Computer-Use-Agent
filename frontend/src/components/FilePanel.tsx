import { Upload, Cloud, X } from "lucide-react";
import { Card } from "@/components/ui/card";
import { useApp } from "@/contexts/AppContext";
import { useState, useRef } from "react";
import { apiService } from "@/lib/api";
import { toast } from "sonner";

const FilePanel = () => {
  const { currentSession } = useApp();
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (file: File) => {
    if (!currentSession) {
      toast.error("Please create a session first");
      return;
    }

    try {
      await apiService.uploadFile(currentSession.id, file);
      toast.success(`File "${file.name}" uploaded successfully`);
    } catch (error) {
      toast.error("Failed to upload file");
      console.error("Error uploading file:", error);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="h-full bg-file-bg border-l border-border flex flex-col">
      {/* File Management Header */}
      <div className="p-4 border-b border-border flex-shrink-0">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium text-foreground">File Management</h3>
          <button className="text-muted-foreground hover:text-foreground">
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Drag and Drop Area */}
      <div className="flex-1 p-4 overflow-y-auto min-h-0">
        <Card 
          className={`relative border-2 border-dashed p-8 text-center transition-colors cursor-pointer ${
            isDragOver 
              ? "border-primary bg-primary/5" 
              : "border-border bg-background/50 hover:border-primary/50"
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={handleClick}
        >
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            onChange={handleFileSelect}
            accept="*/*"
          />
          
          <div className="flex flex-col items-center gap-3">
            <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
              <Cloud className="h-6 w-6 text-primary" />
            </div>
            <div>
              <p className="text-sm font-medium text-foreground mb-1">
                Drag and drop a single file here or click to select a file
              </p>
              <p className="text-xs text-muted-foreground">
                Support for various file formats
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Upload Button Area */}
      <div className="px-4 pb-4">
        <div className="flex items-center justify-center">
          <Upload className="h-4 w-4 text-muted-foreground" />
        </div>
      </div>
    </div>
  );
};

export default FilePanel;
