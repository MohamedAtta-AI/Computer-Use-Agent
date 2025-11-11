import React, { useState } from 'react';
import { Sidebar } from './components/Sidebar/Sidebar';
import { VNCConnection } from './components/VNC/VNCConnection';
import { RightPanel } from './components/RightPanel/RightPanel';
import { useTasks } from './hooks/useTasks';
import { useChat } from './hooks/useChat';
import { useFiles } from './hooks/useFiles';

function App() {
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);
  
  const { 
    tasks, 
    addTask, 
    deleteTask,
    startTask,
    loading: tasksLoading,
    error: tasksError,
    selectedTaskId: tasksSelectedId,
    setSelectedTaskId: setTasksSelectedId,
    refreshTasks
  } = useTasks();

  const { 
    messages, 
    inputValue, 
    setInputValue, 
    sendMessage: sendMessageOriginal,
    stopAgent,
    loading: chatLoading,
    error: chatError,
    agentRunning,
    refreshMessages
  } = useChat(selectedTaskId || undefined);

  // Wrap sendMessage to refresh tasks after sending
  const sendMessage = (content: string) => {
    sendMessageOriginal(content, refreshTasks);
  };

  const { 
    files, 
    addFile, 
    handleDrop, 
    handleDragOver, 
    handleFileUpload: handleFileUploadFromHook,
    uploading: filesUploading,
    error: filesError,
    uploadFile
  } = useFiles(selectedTaskId || undefined);

  const handleNewTask = async () => {
    try {
      const newTask = await addTask({
        title: 'New Agent Task',
        description: 'Task created from UI',
        timestamp: 'just now'
      });
      
      // Select the new task
      setSelectedTaskId(newTask.id);
      setTasksSelectedId(newTask.id);
    } catch (error) {
      console.error('Failed to create new task:', error);
    }
  };

  const handlePromptSelect = (prompt: string) => {
    if (selectedTaskId) {
      sendMessage(prompt);
    } else {
      // Generate a title from the prompt (truncate if too long)
      const generateTitle = (text: string, maxLength: number = 50) => {
        const cleaned = text.trim();
        if (cleaned.length <= maxLength) {
          return cleaned;
        }
        const truncated = cleaned.substring(0, maxLength);
        const lastSpace = truncated.lastIndexOf(' ');
        return lastSpace > maxLength * 0.7 
          ? truncated.substring(0, lastSpace) + '...'
          : truncated + '...';
      };
      
      // Create a new task with a title generated from the prompt
      addTask({
        title: generateTitle(prompt),
        description: prompt,
        timestamp: 'just now'
      }).then(newTask => {
        setSelectedTaskId(newTask.id);
        setTasksSelectedId(newTask.id);
        // Send the prompt after task is created
        setTimeout(() => sendMessage(prompt), 100);
      });
    }
  };

  const handleTaskClick = (task: any) => {
    console.log('Selected task:', task);
    console.log('Previous selectedTaskId:', selectedTaskId);
    console.log('New selectedTaskId:', task.id);
    
    setSelectedTaskId(task.id);
    setTasksSelectedId(task.id);
    
    console.log('Task selection completed');
  };

  const handleTaskDelete = async (taskId: string) => {
    try {
      await deleteTask(taskId);
      console.log('Task deleted successfully:', taskId);
    } catch (error) {
      console.error('Failed to delete task:', error);
    }
  };

  const handleFileUpload = (uploadedFiles: File[]) => {
    uploadedFiles.forEach(file => {
      uploadFile(file);
    });
  };

  const handleFileClick = (file: any) => {
    console.log('Selected file:', file);
    // TODO: Implement file preview or actions
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar
        tasks={tasks}
        onTaskClick={handleTaskClick}
        onNewTask={handleNewTask}
        onPromptSelect={handlePromptSelect}
        loading={tasksLoading}
        error={tasksError}
        selectedTaskId={selectedTaskId}
        onTaskDelete={handleTaskDelete}
      />
      
      <VNCConnection />
      
      <RightPanel
        messages={messages}
        files={files}
        inputValue={inputValue}
        onInputChange={setInputValue}
        onSendMessage={sendMessage}
        onStopAgent={stopAgent}
        onFileUpload={handleFileUpload}
        onFileClick={handleFileClick}
        onFileDrop={handleDrop}
        onFileDragOver={handleDragOver}
        loading={chatLoading}
        error={chatError}
        uploading={filesUploading}
        filesError={filesError}
        selectedTaskId={selectedTaskId}
        agentRunning={agentRunning}
      />
    </div>
  );
}

export default App;