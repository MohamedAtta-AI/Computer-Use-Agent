import React from 'react';
import { config } from '../../config';

interface VNCConnectionProps {
  isConnected?: boolean;
}

export const VNCConnection: React.FC<VNCConnectionProps> = ({ 
  isConnected = true
}) => {
  return (
    <div className="flex-1 bg-gray-900 text-white flex flex-col">
      {/* VNC Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center space-x-3">
          <div className="flex space-x-1">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
          </div>
          <span className="text-sm text-gray-300">Virtual Machine</span>
        </div>
      </div>

      {/* VNC Display Area */}
      <div className="flex-1 relative">
        <iframe
          src={`${config.vncUrl}/vnc.html?view_only=1&autoconnect=1&resize=scale`}
          className="w-full h-full border-none"
          allow="fullscreen"
          title="VNC Connection"
        />
      </div>
    </div>
  );
};