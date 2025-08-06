import { useState, useEffect, useCallback } from 'react';
import { ChatMessage, BackendMessage, RealTimeEvent } from '../types';
import { messageAPI, agentAPI } from '../services/api';
import { websocketService } from '../services/websocket';
import { sseService } from '../services/sse';

export const useChat = (taskId?: string) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Helper function to extract text content from event content
  const extractTextContent = (content: any): string => {
    if (typeof content === 'string') {
      return content;
    }
    if (typeof content === 'object' && content !== null) {
      if (content.text) {
        return content.text;
      }
      if (content.content) {
        return extractTextContent(content.content);
      }
      // If it's an object but no text property, stringify it
      return JSON.stringify(content);
    }
    return String(content);
  };

  // Convert backend message to frontend message
  const convertBackendMessage = (backendMessage: BackendMessage): ChatMessage => {
    return {
      id: backendMessage.id,
      type: backendMessage.role === 'user' ? 'user' : 'assistant',
      content: extractTextContent(backendMessage.content),
      timestamp: new Date(backendMessage.created_at).toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
      }),
      ordering: backendMessage.ordering,
    };
  };

  // Load messages for a task
  const loadMessages = useCallback(async (taskId: string) => {
    if (!taskId) return;
    
    try {
      setLoading(true);
      const backendMessages = await messageAPI.getByTask(taskId);
      const frontendMessages = backendMessages
        .sort((a, b) => a.ordering - b.ordering)
        .map(convertBackendMessage);
      setMessages(frontendMessages);
      setError(null);
    } catch (err) {
      setError('Failed to load messages');
      console.error('Error loading messages:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Send message to backend
  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || !taskId) return;

    try {
      setLoading(true);
      
      // Create user message
      const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content,
        timestamp: new Date().toLocaleTimeString([], { 
          hour: '2-digit', 
          minute: '2-digit' 
        }),
    };

      setMessages(prev => [...prev, userMessage]);
    setInputValue('');

      // Send to backend
      await agentAPI.postMessage(taskId, { text: content });

      // Subscribe to real-time updates for this task
      if (websocketService.isConnected()) {
        websocketService.subscribeToTask(taskId);
      }

      // Connect SSE for real-time updates
      sseService.connect(taskId, {
        onMessage: (event: any) => {
          handleRealTimeEvent(event as RealTimeEvent);
        },
        onError: (error) => {
          console.error('SSE error:', error);
        }
      });

    } catch (err) {
      setError('Failed to send message');
      console.error('Error sending message:', err);
    } finally {
      setLoading(false);
    }
  }, [taskId]);

  // Handle real-time events
  const handleRealTimeEvent = useCallback((event: RealTimeEvent) => {
    console.log('Real-time event received:', event);
    console.log('Event type:', event.type);
    console.log('Event content:', event.content);

    switch (event.type) {
      case 'message':
        console.log('Processing message event, role:', event.role);
        const message: ChatMessage = {
          id: Date.now().toString(),
          type: event.role === 'user' ? 'user' : 'assistant',
          content: extractTextContent(event.content),
          timestamp: new Date().toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
          }),
          ordering: event.ordering,
        };
        console.log('Created message object:', message);
        setMessages(prev => {
          console.log('Previous messages:', prev);
          const newMessages = [...prev, message];
          console.log('New messages array:', newMessages);
          return newMessages;
        });
        break;

      case 'event':
        const eventMessage: ChatMessage = {
          id: Date.now().toString(),
          type: 'event',
          content: `Tool execution: ${event.kind}`,
          timestamp: new Date().toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
          }),
          ordering: event.ordering,
          kind: event.kind,
          payload: event.payload,
        };
        setMessages(prev => [...prev, eventMessage]);
        break;

      case 'screenshot':
        const screenshotMessage: ChatMessage = {
          id: Date.now().toString(),
          type: 'screenshot',
          content: 'Screenshot captured',
          timestamp: new Date().toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
          }),
          ordering: event.ordering,
          url: event.url,
          sha256: event.sha256,
        };
        setMessages(prev => [...prev, screenshotMessage]);
        break;

      case 'tool_result':
        const toolResultMessage: ChatMessage = {
          id: Date.now().toString(),
          type: 'function_result',
          content: extractTextContent(event.content),
          timestamp: new Date().toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
          }),
          ordering: event.ordering,
        };
        setMessages(prev => [...prev, toolResultMessage]);
        break;

      case 'error':
        const errorMessage: ChatMessage = {
          id: Date.now().toString(),
        type: 'assistant',
          content: `Error: ${extractTextContent(event.content)}`,
          timestamp: new Date().toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
          }),
          ordering: event.ordering,
        };
        setMessages(prev => [...prev, errorMessage]);
        setError(extractTextContent(event.content));
        break;

      default:
        console.log('Unknown event type:', event.type);
    }
  }, []);

  // Load messages when taskId changes
  useEffect(() => {
    console.log('useChat: taskId changed to:', taskId);
    console.log('useChat: SSE connected tasks:', sseService.getConnectedTasks());
    
    if (taskId) {
      console.log('useChat: Loading messages for task:', taskId);
      loadMessages(taskId);
    } else {
      console.log('useChat: Clearing messages (no taskId)');
      setMessages([]);
    }
  }, [taskId, loadMessages]);

  // Cleanup SSE connection only on component unmount, not on taskId changes
  useEffect(() => {
    return () => {
      // Only disconnect when the component is unmounting, not when taskId changes
      // This prevents the connection from being closed when switching tasks
    };
  }, []); // Empty dependency array - only runs on unmount

  return { 
    messages, 
    inputValue, 
    setInputValue, 
    sendMessage,
    loading,
    error,
    refreshMessages: () => taskId ? loadMessages(taskId) : Promise.resolve()
  };
};