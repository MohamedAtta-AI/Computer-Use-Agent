import { Monitor, Wifi, WifiOff, Settings, Play, Square } from "lucide-react";
import { useApp } from "@/contexts/AppContext";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { toast } from "sonner";
import RealVncDisplay from "./RealVncDisplay";

const VncPanel = () => {
  const { currentSession, ws } = useApp();
  const [vncConnected, setVncConnected] = useState(false);
  const [vncSettings, setVncSettings] = useState({
    host: "localhost",
    port: "5900",
    password: ""
  });
  const [showSettings, setShowSettings] = useState(false);

  const handleConnectionChange = (connected: boolean) => {
    setVncConnected(connected);
  };

  const handleVncConnect = () => {
    if (!vncSettings.host || !vncSettings.port) {
      toast.error("Please enter VNC host and port");
      return;
    }
    
    // For now, simulate VNC connection
    setVncConnected(true);
    toast.success(`Connected to VNC at ${vncSettings.host}:${vncSettings.port}`);
  };

  const handleVncDisconnect = () => {
    setVncConnected(false);
    toast.info("Disconnected from VNC");
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
          {vncConnected ? (
            <Button
              variant="destructive"
              size="sm"
              onClick={handleVncDisconnect}
              className="text-white"
            >
              <Square className="h-4 w-4 mr-1" />
              Disconnect
            </Button>
          ) : (
            <Button
              variant="default"
              size="sm"
              onClick={handleVncConnect}
              className="bg-green-600 hover:bg-green-700 text-white"
            >
              <Play className="h-4 w-4 mr-1" />
              Connect
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
                value={vncSettings.host}
                onChange={(e) => setVncSettings(prev => ({ ...prev, host: e.target.value }))}
                className="bg-gray-600 border-gray-500 text-white"
                placeholder="localhost"
              />
            </div>
            <div>
              <label className="text-white text-xs mb-1 block">Port</label>
              <Input
                value={vncSettings.port}
                onChange={(e) => setVncSettings(prev => ({ ...prev, port: e.target.value }))}
                className="bg-gray-600 border-gray-500 text-white"
                placeholder="5900"
              />
            </div>
            <div>
              <label className="text-white text-xs mb-1 block">Password (optional)</label>
              <Input
                type="password"
                value={vncSettings.password}
                onChange={(e) => setVncSettings(prev => ({ ...prev, password: e.target.value }))}
                className="bg-gray-600 border-gray-500 text-white"
                placeholder="VNC password"
              />
            </div>
          </div>
        </Card>
      )}

            {/* VNC Display Area */}
      <div className="flex-1 flex items-center justify-center relative">
        {currentSession ? (
          <RealVncDisplay 
            sessionId={currentSession.id} 
            onConnectionChange={handleConnectionChange}
          />
        ) : (
          <div className="text-center text-white/60">
            <Monitor className="h-16 w-16 mx-auto mb-4 opacity-60" />
            <p className="text-lg">VNC Connection</p>
            <p className="text-sm opacity-80 mb-4">Create a session to connect to VNC</p>
            
            {/* Connection Status */}
            <div className="flex items-center justify-center gap-2 mb-4">
              {ws?.readyState === WebSocket.OPEN ? (
                <>
                  <Wifi className="h-4 w-4 text-green-400" />
                  <span className="text-sm text-green-400">WebSocket Connected</span>
                </>
              ) : (
                <>
                  <WifiOff className="h-4 w-4 text-red-400" />
                  <span className="text-sm text-red-400">WebSocket Disconnected</span>
                </>
              )}
            </div>
          </div>
        )}
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

export default VncPanel;
