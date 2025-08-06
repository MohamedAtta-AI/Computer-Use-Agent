import React from 'react';
import { Plus } from 'lucide-react';

interface NewTaskButtonProps {
  onClick?: () => void;
}

export const NewTaskButton: React.FC<NewTaskButtonProps> = ({ onClick }) => {
  return (
    <div className="p-4">
      <button
        onClick={onClick}
        className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
      >
        <Plus className="w-4 h-4" />
        <span>Start New Agent Task</span>
      </button>
    </div>
  );
};