import { useState, useEffect, useRef } from "react";
import { Monitor, Maximize2, Play, Square } from "lucide-react";
import { Button } from "@/components/ui/button";

interface VNCPanelProps {
  className?: string;
}

export function VNCPanel({ className = "" }: VNCPanelProps) {
  const [isConnected, setIsConnected] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const connectVNC = () => {
    if (wsRef.current) return;
    
    const ws = new WebSocket('ws://localhost:8000/api/vnc');
    wsRef.current = ws;
    
    ws.onopen = () => {
      setIsConnected(true);
      console.log('VNC connected');
    };
    
    ws.onclose = () => {
      setIsConnected(false);
      wsRef.current = null;
      console.log('VNC disconnected');
    };
    
    ws.onerror = (error) => {
      console.error('VNC error:', error);
      setIsConnected(false);
    };
  };

  const disconnectVNC = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  };

  useEffect(() => {
    // Auto-connect on mount
    connectVNC();
    
    return () => {
      disconnectVNC();
    };
  }, []);

  return (
    <div className={`bg-card border-r border-panel-border flex flex-col ${className}`}>
      {/* VNC Toolbar */}
      <div className="p-3 border-b border-panel-border bg-muted/30">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Monitor className="h-4 w-4" />
            Virtual Machine Connection
            {isConnected && (
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            )}
          </div>
          <div className="flex gap-2">
            <Button 
              variant="ghost" 
              size="sm"
              onClick={isConnected ? disconnectVNC : connectVNC}
            >
              {isConnected ? <Square className="h-4 w-4" /> : <Play className="h-4 w-4" />}
            </Button>
            <Button 
              variant="ghost" 
              size="sm"
              onClick={() => setIsFullscreen(!isFullscreen)}
            >
              <Maximize2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* VNC Display Area */}
      <div className="flex-1 bg-vnc-background relative overflow-hidden">
        {isConnected ? (
          <canvas 
            ref={canvasRef}
            className="w-full h-full"
            style={{ cursor: 'crosshair' }}
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center text-white/60">
              <Monitor className="h-12 w-12 mx-auto mb-4 opacity-40" />
              <p className="text-sm">VNC Connection</p>
              <p className="text-xs opacity-60 mt-1">Click play to connect</p>
            </div>
          </div>
        )}

        {/* Desktop taskbar */}
        <div className="absolute bottom-0 left-0 right-0 h-10 bg-black/90 flex items-center px-2">
          <div className="text-white text-xs">Workspace 1</div>
          <div className="flex-1" />
          <div className="flex gap-1">
            <div className="w-8 h-6 bg-green-600/80 rounded-sm"></div>
            <div className="w-8 h-6 bg-orange-600/80 rounded-sm"></div>
            <div className="w-8 h-6 bg-red-600/80 rounded-sm"></div>
            <div className="w-8 h-6 bg-blue-600/80 rounded-sm"></div>
            <div className="w-8 h-6 bg-gray-600/80 rounded-sm"></div>
            <div className="w-8 h-6 bg-purple-600/80 rounded-sm"></div>
          </div>
        </div>
      </div>
    </div>
  );
}