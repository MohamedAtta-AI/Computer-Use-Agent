import { useState, useEffect, useCallback } from 'react';
import { Task, BackendTask } from '../types';
import { taskAPI } from '../services/api';
import { websocketService } from '../services/websocket';
import { sseService } from '../services/sse';

export const useTasks = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);

  // Convert backend task to frontend task
  const convertBackendTask = (backendTask: BackendTask): Task => {
    return {
      id: backendTask.id,
      title: backendTask.title,
      description: `Task created on ${new Date(backendTask.created_at).toLocaleDateString()}`,
      status: backendTask.status as Task['status'],
      timestamp: new Date(backendTask.created_at).toLocaleString(),
    };
  };

  // Load tasks from backend
  const loadTasks = useCallback(async () => {
    try {
      setLoading(true);
      const backendTasks = await taskAPI.getAll();
      const frontendTasks = backendTasks.map(convertBackendTask);
      setTasks(frontendTasks);
      setError(null);
    } catch (err) {
      setError('Failed to load tasks');
      console.error('Error loading tasks:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Create new task
  const addTask = useCallback(async (taskData: Omit<Task, 'id'>) => {
    try {
      const backendTask = await taskAPI.create({
        title: taskData.title,
        status: taskData.status || 'active',
      });
      const newTask = convertBackendTask(backendTask);
      setTasks(prev => [newTask, ...prev]);
      return newTask;
    } catch (err) {
      setError('Failed to create task');
      console.error('Error creating task:', err);
      throw err;
    }
  }, []);

  // Update task status
  const updateTaskStatus = useCallback(async (id: string, status: Task['status']) => {
    try {
      await taskAPI.update(id, { status });
      setTasks(prev => prev.map(task => 
        task.id === id ? { ...task, status } : task
      ));
    } catch (err) {
      setError('Failed to update task');
      console.error('Error updating task:', err);
    }
  }, []);

  // Start task execution
  const startTask = useCallback(async (id: string) => {
    try {
      await taskAPI.start(id);
      await updateTaskStatus(id, 'running');
      
      // Subscribe to real-time updates for this task
      if (websocketService.isConnected()) {
        websocketService.subscribeToTask(id);
      }
      
      // Also connect SSE for this task
      sseService.connect(id, {
        onMessage: (event) => {
          console.log('SSE event received:', event);
          // Handle real-time updates
          handleRealTimeEvent(id, event);
        },
        onError: (error) => {
          console.error('SSE error:', error);
        }
      });
      
    } catch (err) {
      setError('Failed to start task');
      console.error('Error starting task:', err);
    }
  }, [updateTaskStatus]);

  // Handle real-time events
  const handleRealTimeEvent = useCallback((taskId: string, event: any) => {
    // Update task status based on events
    if (event.type === 'message' && event.role === 'assistant') {
      // Task is active when receiving assistant messages
      updateTaskStatus(taskId, 'running');
    }
    
    // You can add more event handling logic here
    console.log(`Real-time event for task ${taskId}:`, event);
  }, [updateTaskStatus]);

  // Initialize WebSocket connection only once on mount
  useEffect(() => {
    websocketService.connect({
      onMessage: (message) => {
        console.log('WebSocket message received:', message);
        if (message.type === 'subscribed') {
          console.log(`Subscribed to task: ${message.task_id}`);
        }
      },
      onOpen: () => {
        console.log('WebSocket connected');
        // Subscribe to selected task if any
        if (selectedTaskId) {
          websocketService.subscribeToTask(selectedTaskId);
        }
      },
      onError: (error) => {
        console.error('WebSocket error:', error);
      }
    });

    // Cleanup only on component unmount
    return () => {
      websocketService.disconnect();
      sseService.disconnect();
    };
  }, []); // Remove selectedTaskId dependency

  // Subscribe to selected task when it changes
  useEffect(() => {
    console.log('useTasks: selectedTaskId changed to:', selectedTaskId);
    console.log('useTasks: WebSocket connected:', websocketService.isConnected());
    console.log('useTasks: SSE connected tasks:', sseService.getConnectedTasks());
    
    if (selectedTaskId && websocketService.isConnected()) {
      console.log('useTasks: Subscribing to task via WebSocket:', selectedTaskId);
      websocketService.subscribeToTask(selectedTaskId);
    }
  }, [selectedTaskId]);

  // Load tasks on mount
  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  return { 
    tasks, 
    addTask, 
    updateTaskStatus, 
    startTask,
    loading,
    error,
    selectedTaskId,
    setSelectedTaskId,
    refreshTasks: loadTasks
  };
};