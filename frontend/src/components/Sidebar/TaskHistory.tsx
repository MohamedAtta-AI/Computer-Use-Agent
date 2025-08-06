import React from 'react';
import { Task } from '../../types';
import { CheckCircle, Clock, XCircle, Loader2, Trash2, Play } from 'lucide-react';

interface TaskHistoryProps {
  tasks: Task[];
  onTaskClick?: (task: Task) => void;
  onTaskDelete?: (taskId: string) => void;
  loading?: boolean;
  error?: string | null;
  selectedTaskId?: string | null;
}

const statusConfig = {
  inactive: {
    icon: Clock,
    color: 'text-gray-500',
    bgColor: 'bg-gray-100',
    label: 'Inactive'
  },
  active: {
    icon: Play,
    color: 'text-blue-500',
    bgColor: 'bg-blue-100',
    label: 'Active'
  },
  completed: {
    icon: CheckCircle,
    color: 'text-green-500',
    bgColor: 'bg-green-100',
    label: 'Finished'
  },
  running: {
    icon: Loader2,
    color: 'text-blue-500',
    bgColor: 'bg-blue-100',
    label: 'Running'
  },
  failed: {
    icon: XCircle,
    color: 'text-red-500',
    bgColor: 'bg-red-100',
    label: 'Failed'
  }
};

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

  const getStatusConfig = (status: string) => {
    // Map backend statuses to our display configs
    switch (status) {
      case 'active':
        return statusConfig.active;
      case 'completed':
        return statusConfig.completed;
      case 'running':
        return statusConfig.running;
      case 'failed':
        return statusConfig.failed;
      default:
        return statusConfig.inactive; // Default for new tasks
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
          <Loader2 className="w-4 h-4 animate-spin text-gray-500" />
          <span className="ml-2 text-sm text-gray-500">Loading tasks...</span>
        </div>
      )}
      
      <div className="space-y-2">
        {tasks.map((task) => {
          const config = getStatusConfig(task.status);
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
                <div className="flex items-center space-x-2">
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${config.bgColor} ${config.color}`}>
                    {config.label}
                  </span>
                  <button
                    onClick={(e) => handleDeleteClick(e, task.id)}
                    className="p-1 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded transition-colors"
                    title="Delete task"
                  >
                    <Trash2 className="w-3 h-3" />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};