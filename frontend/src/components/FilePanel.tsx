import { useState, useEffect, useCallback } from "react";
import {
  Upload,
  File as FileIcon,
  FolderOpen,
  Download,
  Trash2,
  CloudUpload,
} from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card } from "@/components/ui/card";

import { uploadFile } from "@/lib/api";

/* ------------------------------------------------------------------ */
/* Types */
/* ------------------------------------------------------------------ */

interface FileItem {
  id: string;
  name: string;
  type: "file" | "folder";
  size?: string;
  uploadDate: Date;
  url?: string;
}

interface FilePanelProps {
  sessionId?: string;
  className?: string;
}

/* ------------------------------------------------------------------ */
/* Component */
/* ------------------------------------------------------------------ */

export function FilePanel({ sessionId, className = "" }: FilePanelProps) {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [dragActive, setDragActive] = useState(false);

  /* ------------------------- handlers ----------------------------- */
  const addFileMeta = (meta: Partial<FileItem>) =>
    setFiles((prev) => [
      ...prev,
      {
        id: meta.id ?? crypto.randomUUID(),
        name: meta.name ?? "unknown",
        type: "file",
        uploadDate: new Date(),
        url: meta.url,
        size: meta.size,
      },
    ]);

  const doUpload = useCallback(
    async (file: File) => {
      if (!sessionId) {
        alert("No session yet – start a task first.");
        return;
      }
      try {
        const meta = await uploadFile(file, sessionId);
        addFileMeta({ ...meta, uploadDate: new Date() });
      } catch (err) {
        console.error("Upload failed:", err);
      }
    },
    [sessionId]
  );

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === "dragenter" || e.type === "dragover");
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const f = e.dataTransfer.files?.[0];
    if (f) doUpload(f);
  };

  const pickFile = () => {
    const input = document.createElement("input");
    input.type = "file";
    input.onchange = (ev) => {
      const f = (ev.target as HTMLInputElement).files?.[0];
      if (f) doUpload(f);
    };
    input.click();
  };

  /* --------------------------- render ----------------------------- */
  const formatDate = (d: Date) =>
    d.toLocaleDateString([], { month: "short", day: "numeric" });

  return (
    <div className={`bg-card flex flex-col min-h-0 ${className}`}>
      {/* header */}
      <div className="p-4 border-b border-panel-border">
        <h3 className="text-sm font-medium text-foreground">File Management</h3>
      </div>

      {/* list */}
      <ScrollArea className="flex-1 min-h-0">
        <div className="p-4 space-y-2">
          {files.length === 0 && (
            <p className="text-xs text-muted-foreground">
              No files uploaded yet.
            </p>
          )}
          {files.map((f) => (
            <Card key={f.id} className="p-2 flex items-center gap-2">
              {f.type === "folder" ? (
                <FolderOpen className="h-4 w-4 text-blue-500" />
              ) : (
                <FileIcon className="h-4 w-4 text-gray-500" />
              )}
              <span className="flex-1 truncate text-sm">{f.name}</span>
              <span className="text-xs text-muted-foreground">
                {formatDate(f.uploadDate)}
              </span>
              {f.url && (
                <a
                  href={f.url}
                  download
                  className="hover:text-agent-blue"
                  title="Download"
                >
                  <Download className="h-4 w-4" />
                </a>
              )}
              <button
                onClick={() =>
                  setFiles((prev) => prev.filter((x) => x.id !== f.id))
                }
                title="Remove"
                className="text-red-600 hover:text-red-800"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </Card>
          ))}
        </div>
      </ScrollArea>

      {/* drag-drop zone */}
      <div
        className={`m-4 mt-0 flex flex-col items-center justify-center border-2 border-dashed rounded-lg cursor-pointer transition-colors ${
          dragActive
            ? "border-agent-blue bg-agent-blue/5"
            : "border-muted-foreground/25 hover:border-muted-foreground/50"
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={pickFile}
        style={{ minHeight: 140 }}
      >
        <CloudUpload className="h-10 w-10 mb-2 text-muted-foreground" />
        <p className="text-sm font-medium text-foreground">Upload Files</p>
        <p className="text-xs text-muted-foreground">
          Drag &amp; drop or click to select
        </p>
      </div>
    </div>
  );
}
