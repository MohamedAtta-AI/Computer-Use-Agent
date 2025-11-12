// Frontend configuration from environment variables
// All Vite environment variables must be prefixed with VITE_
export const config = {
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  vncUrl: import.meta.env.VITE_VNC_URL || 'http://localhost:6080',
  wsUrl: import.meta.env.VITE_WS_URL || 'ws://localhost:8000',
} as const;

