import React from 'react';
import { Task } from '../../types';
import { CheckCircle, Clock, XCircle, Loader2 } from 'lucide-react';

interface TaskHistoryProps {
  tasks: Task[];
  onTaskClick?: (task: Task) => void;
  loading?: boolean;
  error?: string | null;
  selectedTaskId?: string | null;
}

const statusConfig = {
  completed: {
    icon: CheckCircle,
    color: 'text-green-500',
    bgColor: 'bg-green-100'
  },
  running: {
    icon: Clock,
    color: 'text-blue-500',
    bgColor: 'bg-blue-100'
  },
  failed: {
    icon: XCircle,
    color: 'text-red-500',
    bgColor: 'bg-red-100'
  },
  active: {
    icon: Clock,
    color: 'text-gray-500',
    bgColor: 'bg-gray-100'
  }
};

export const TaskHistory: React.FC<TaskHistoryProps> = ({ 
  tasks, 
  onTaskClick,
  loading = false,
  error = null,
  selectedTaskId = null
}) => {
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
          <Loader2 className="w-4 h-4 animate-spin text-gray-500" />
          <span className="ml-2 text-sm text-gray-500">Loading tasks...</span>
        </div>
      )}
      
      <div className="space-y-2">
        {tasks.map((task) => {
          const config = statusConfig[task.status];
          const Icon = config.icon;
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
                <div className={`p-1 rounded-full ${config.bgColor}`}>
                  <Icon className={`w-3 h-3 ${config.color}`} />
                </div>
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
                <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium capitalize ${config.bgColor} ${config.color}`}>
                  {task.status}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};