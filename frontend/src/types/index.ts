// Backend API Types
export interface BackendTask {
  id: string;
  title: string;
  status: string;
  created_at: string;
}

export interface BackendMessage {
  id: string;
  task_id: string;
  role: string;
  content: any;
  ordering: number;
  created_at: string;
}

export interface BackendEvent {
  id: string;
  task_id: string;
  kind: string;
  ordering: number;
  payload: any;
  created_at: string;
}

export interface BackendScreenshot {
  id: string;
  event_id: string;
  url: string;
  sha256: string;
}

export interface BackendMedia {
  id: string;
  task_id: string;
  uploaded_by: string;
  filename: string;
  content_type: string;
  url: string;
  sha256: string;
  created_at: string;
}

// Frontend UI Types
export interface Task {
  id: string;
  title: string;
  description: string;
  timestamp: string;
  duration?: string;
}

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant' | 'function_call' | 'function_result' | 'event' | 'screenshot';
  content: string | any;
  timestamp: string;
  functionName?: string;
  ordering?: number;
  url?: string;
  sha256?: string;
  kind?: string;
  payload?: any;
}

export interface FileItem {
  id: string;
  name: string;
  type: 'file' | 'folder';
  size?: string;
  timestamp: string;
}

export interface VNCConnectionProps {
  isConnected: boolean;
  onConnect?: () => void;
  onDisconnect?: () => void;
}

// Real-time Event Types
export interface RealTimeEvent {
  type: 'message' | 'event' | 'screenshot' | 'tool_result' | 'error' | 'completion';
  role?: string;
  content?: any;
  ordering?: number;
  url?: string;
  sha256?: string;
  kind?: string;
  payload?: any;
}

export interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

export interface SSEEvent {
  type: string;
  [key: string]: any;
}