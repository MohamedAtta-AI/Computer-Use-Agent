import React from 'react';
import { Monitor, Settings } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <div className="flex items-center justify-between p-4 border-b border-gray-200">
      <div className="flex items-center space-x-2">
        <Monitor className="w-5 h-5 text-blue-600" />
        <h1 className="text-lg font-semibold text-gray-900">Agent Control Center</h1>
      </div>
      <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
        <Settings className="w-4 h-4 text-gray-500" />
      </button>
    </div>
  );
};