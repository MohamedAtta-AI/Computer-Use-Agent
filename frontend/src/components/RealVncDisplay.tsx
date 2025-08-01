import React, { useEffect, useRef, useState } from 'react';
import { Monitor, Wifi, WifiOff, Settings, Play, Square, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { toast } from "sonner";
import { apiService } from "@/lib/api";

interface VNCConnectionInfo {
  host: string;
  port: number;
  password?: string;
  is_connected?: boolean;
  vnc_url?: string;
  websocket_url?: string;
}

interface RealVncDisplayProps {
  sessionId: number;
  onConnectionChange?: (connected: boolean) => void;
}

const RealVncDisplay: React.FC<RealVncDisplayProps> = ({ sessionId, onConnectionChange }) => {
  const [vncInfo, setVncInfo] = useState<VNCConnectionInfo | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [settings, setSettings] = useState({
    host: "localhost",
    port: "5900",
    password: ""
  });
  const vncFrameRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    loadVncConnection();
  }, [sessionId]);

  const loadVncConnection = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/vnc/connection/${sessionId}`);
      if (response.ok) {
        const data = await response.json();
        setVncInfo(data);
        onConnectionChange?.(data.is_connected || false);
      }
    } catch (error) {
      console.error("Failed to load VNC connection:", error);
    }
  };

  const handleConnect = async () => {
    if (!settings.host || !settings.port) {
      toast.error("Please enter VNC host and port");
      return;
    }

    setIsConnecting(true);
    try {
      const response = await fetch(`http://localhost:8000/api/v1/vnc/connection/${sessionId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          host: settings.host,
          port: parseInt(settings.port),
          password: settings.password || undefined,
          session_id: sessionId
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setVncInfo(data);
        onConnectionChange?.(data.is_connected || false);
        
        if (data.is_connected) {
          toast.success(`Connected to VNC at ${settings.host}:${settings.port}`);
          setShowSettings(false);
        } else {
          toast.error("Failed to connect to VNC server");
        }
      } else {
        toast.error("Failed to establish VNC connection");
      }
    } catch (error) {
      console.error("VNC connection error:", error);
      toast.error("VNC connection failed");
    } finally {
      setIsConnecting(false);
    }
  };

  const handleDisconnect = async () => {
    try {
      await fetch(`http://localhost:8000/api/v1/vnc/connection/${sessionId}`, {
        method: 'DELETE',
      });
      setVncInfo(null);
      onConnectionChange?.(false);
      toast.info("Disconnected from VNC");
    } catch (error) {
      console.error("Failed to disconnect:", error);
    }
  };

  const renderVncDisplay = () => {
    if (!vncInfo?.is_connected) {
      return (
        <div className="text-center text-white/60">
          <Monitor className="h-16 w-16 mx-auto mb-4 opacity-60" />
          <p className="text-lg">VNC Connection</p>
          <p className="text-sm opacity-80 mb-4">Connect to a virtual machine to see the display</p>
          
          <div className="flex items-center justify-center gap-2 mb-4">
            <WifiOff className="h-4 w-4 text-red-400" />
            <span className="text-sm text-red-400">Not Connected</span>
          </div>
        </div>
      );
    }

    // If we have a noVNC URL, embed it like the original setup
    if (vncInfo.novnc_url) {
      return (
        <div className="w-full h-full">
          <iframe
            ref={vncFrameRef}
            src={vncInfo.novnc_url}
            className="w-full h-full border-0"
            title="VNC Display"
            allow="fullscreen"
          />
        </div>
      );
    }

    // Fallback to connection info
    return (
      <div className="text-center text-white/60">
        <div className="w-96 h-64 bg-gray-800 border-2 border-gray-600 rounded-lg flex items-center justify-center mb-4">
          <div className="text-center">
            <Monitor className="h-12 w-12 mx-auto mb-2 opacity-60" />
            <p className="text-sm">VNC Display Area</p>
            <p className="text-xs opacity-60 mt-1">Connected to {vncInfo.host}:{vncInfo.port}</p>
          </div>
        </div>
        <div className="flex items-center justify-center gap-2">
          <Wifi className="h-4 w-4 text-green-400" />
          <span className="text-sm text-green-400">VNC Connected</span>
        </div>
        <div className="mt-2 text-xs opacity-60">
          <p>VNC URL: {vncInfo.vnc_url}</p>
          {vncInfo.websocket_url && <p>WebSocket: {vncInfo.websocket_url}</p>}
        </div>
      </div>
    );
  };

  return (
    <div className="flex-1 bg-vnc-bg relative flex flex-col">
      {/* VNC Header */}
      <div className="bg-gray-800 px-4 py-2 flex items-center justify-between border-b border-gray-700">
        <div className="flex items-center gap-2">
          <Monitor className="h-4 w-4 text-white" />
          <span className="text-white text-sm font-medium">Virtual Machine</span>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowSettings(!showSettings)}
            className="text-white hover:bg-gray-700"
          >
            <Settings className="h-4 w-4" />
          </Button>
          {vncInfo?.is_connected ? (
            <Button
              variant="destructive"
              size="sm"
              onClick={handleDisconnect}
              className="text-white"
            >
              <Square className="h-4 w-4 mr-1" />
              Disconnect
            </Button>
          ) : (
            <Button
              variant="default"
              size="sm"
              onClick={handleConnect}
              disabled={isConnecting}
              className="bg-green-600 hover:bg-green-700 text-white"
            >
              <Play className="h-4 w-4 mr-1" />
              {isConnecting ? "Connecting..." : "Connect"}
            </Button>
          )}
        </div>
      </div>

      {/* VNC Settings Panel */}
      {showSettings && (
        <Card className="m-4 p-4 bg-gray-700 border-gray-600">
          <h3 className="text-white text-sm font-medium mb-3">VNC Connection Settings</h3>
          <div className="space-y-3">
            <div>
              <label className="text-white text-xs mb-1 block">Host</label>
              <Input
                value={settings.host}
                onChange={(e) => setSettings(prev => ({ ...prev, host: e.target.value }))}
                className="bg-gray-600 border-gray-500 text-white"
                placeholder="localhost"
              />
            </div>
            <div>
              <label className="text-white text-xs mb-1 block">Port</label>
              <Input
                value={settings.port}
                onChange={(e) => setSettings(prev => ({ ...prev, port: e.target.value }))}
                className="bg-gray-600 border-gray-500 text-white"
                placeholder="5900"
              />
            </div>
            <div>
              <label className="text-white text-xs mb-1 block">Password (optional)</label>
              <Input
                type="password"
                value={settings.password}
                onChange={(e) => setSettings(prev => ({ ...prev, password: e.target.value }))}
                className="bg-gray-600 border-gray-500 text-white"
                placeholder="VNC password"
              />
            </div>
          </div>
        </Card>
      )}

      {/* VNC Display Area */}
      <div className="flex-1 flex items-center justify-center relative">
        {renderVncDisplay()}
      </div>
      
      {/* Bottom taskbar simulation */}
      <div className="absolute bottom-0 left-0 right-0 bg-gray-900 h-12 flex items-center px-4">
        <span className="text-white text-sm">Workspace 1</span>
        <div className="flex ml-auto space-x-2">
          {/* Simulated taskbar icons */}
          <div className="w-8 h-8 bg-green-600 rounded flex items-center justify-center">
            <div className="w-4 h-4 bg-white rounded-sm" />
          </div>
          <div className="w-8 h-8 bg-gray-600 rounded flex items-center justify-center">
            <div className="w-4 h-4 bg-gray-300 rounded-sm" />
          </div>
          <div className="w-8 h-8 bg-red-600 rounded flex items-center justify-center">
            <div className="w-4 h-4 bg-white rounded-full" />
          </div>
          <div className="w-8 h-8 bg-orange-600 rounded flex items-center justify-center">
            <div className="w-4 h-4 bg-white" />
          </div>
          <div className="w-8 h-8 bg-red-800 rounded flex items-center justify-center">
            <div className="w-3 h-3 bg-white" />
          </div>
          <div className="w-8 h-8 bg-gray-700 rounded flex items-center justify-center">
            <div className="w-4 h-4 bg-blue-400 rounded-sm" />
          </div>
          <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center">
            <div className="w-4 h-4 bg-white grid grid-cols-2 gap-px">
              <div className="bg-blue-600"></div>
              <div className="bg-blue-600"></div>
              <div className="bg-blue-600"></div>
              <div className="bg-blue-600"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RealVncDisplay; 