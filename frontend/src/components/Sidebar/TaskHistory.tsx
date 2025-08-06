import React from 'react';
import { Task } from '../../types';
import { Trash2 } from 'lucide-react';

interface TaskHistoryProps {
  tasks: Task[];
  onTaskClick?: (task: Task) => void;
  onTaskDelete?: (taskId: string) => void;
  loading?: boolean;
  error?: string | null;
  selectedTaskId?: string | null;
}

export const TaskHistory: React.FC<TaskHistoryProps> = ({ 
  tasks, 
  onTaskClick,
  onTaskDelete,
  loading = false,
  error = null,
  selectedTaskId = null
}) => {
  const handleDeleteClick = (e: React.MouseEvent, taskId: string) => {
    e.stopPropagation(); // Prevent task selection when clicking delete
    if (onTaskDelete) {
      onTaskDelete(taskId);
    }
  };

  return (
    <div className="px-4 py-3">
      <h2 className="text-sm font-medium text-gray-700 mb-3">Task History</h2>
      
      {error && (
        <div className="mb-3 p-2 bg-red-50 border border-red-200 rounded">
          <p className="text-xs text-red-600">{error}</p>
        </div>
      )}
      
      {loading && (
        <div className="flex items-center justify-center py-4">
          <div className="w-4 h-4 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin"></div>
          <span className="ml-2 text-sm text-gray-500">Loading tasks...</span>
        </div>
      )}
      
      <div className="space-y-2">
        {tasks.map((task) => {
          const isSelected = selectedTaskId === task.id;
          
          return (
            <div
              key={task.id}
              onClick={() => onTaskClick?.(task)}
              className={`p-3 bg-white border rounded-lg hover:shadow-sm transition-shadow cursor-pointer ${
                isSelected 
                  ? 'border-blue-500 bg-blue-50' 
                  : 'border-gray-200'
              }`}
            >
              <div className="flex items-start space-x-3">
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-medium text-gray-900 truncate">
                    {task.title}
                  </h3>
                  <p className="text-xs text-gray-500 mt-1">
                    {task.description}
                  </p>
                  <p className="text-xs text-gray-400 mt-1">
                    {task.timestamp}
                  </p>
                </div>
                <button
                  onClick={(e) => handleDeleteClick(e, task.id)}
                  className="p-1 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded transition-colors"
                  title="Delete task"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};