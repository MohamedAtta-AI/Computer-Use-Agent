import React, { useState } from 'react';
import { Header } from './Header';
import { SearchInput } from './SearchInput';
import { TaskHistory } from './TaskHistory';
import { PromptGallery } from './PromptGallery';
import { NewTaskButton } from './NewTaskButton';
import { Task } from '../../types';

interface SidebarProps {
  tasks: Task[];
  onTaskClick?: (task: Task) => void;
  onTaskDelete?: (taskId: string) => void;
  onNewTask?: () => void;
  onPromptSelect?: (prompt: string) => void;
  loading?: boolean;
  error?: string | null;
  selectedTaskId?: string | null;
}

export const Sidebar: React.FC<SidebarProps> = ({
  tasks,
  onTaskClick,
  onTaskDelete,
  onNewTask,
  onPromptSelect,
  loading = false,
  error = null,
  selectedTaskId = null
}) => {
  const [searchValue, setSearchValue] = useState('');

  const filteredTasks = tasks.filter(task =>
    task.title.toLowerCase().includes(searchValue.toLowerCase()) ||
    task.description.toLowerCase().includes(searchValue.toLowerCase())
  );

  return (
    <div className="w-80 bg-white border-r border-gray-200 flex flex-col h-screen">
      <Header />
      <SearchInput value={searchValue} onChange={setSearchValue} />
      <div className="flex-1 overflow-y-auto">
        <TaskHistory 
          tasks={filteredTasks} 
          onTaskClick={onTaskClick}
          loading={loading}
          error={error}
          selectedTaskId={selectedTaskId}
          onTaskDelete={onTaskDelete}
        />
        <PromptGallery onPromptSelect={onPromptSelect} />
      </div>
      <NewTaskButton onClick={onNewTask} />
    </div>
  );
};