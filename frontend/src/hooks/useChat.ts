import { useState, useEffect, useCallback } from 'react';
import { ChatMessage, BackendMessage, RealTimeEvent } from '../types';
import { messageAPI, agentAPI, taskAPI } from '../services/api';
import { websocketService } from '../services/websocket';
import { sseService } from '../services/sse';

export const useChat = (taskId?: string) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [agentRunning, setAgentRunning] = useState(false);

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
      return JSON.stringify(content);
    }
    return String(content);
  };

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

  // Load messages for the current task
  useEffect(() => {
    if (!taskId) {
      setMessages([]);
      return;
    }

    const loadMessages = async () => {
      try {
        setLoading(true);
        const backendMessages = await messageAPI.getByTask(taskId);
        const chatMessages = backendMessages.map(convertBackendMessage);
        setMessages(chatMessages);
        setError(null);
      } catch (err) {
        setError('Failed to load messages');
        console.error('Error loading messages:', err);
      } finally {
        setLoading(false);
      }
    };

    loadMessages();
  }, [taskId]);

  // Send message and start agent
  const sendMessage = useCallback(async (content: string, onTaskUpdate?: () => void) => {
    if (!taskId || !content.trim() || loading) return;

    try {
      setLoading(true);
      setError(null);
      setAgentRunning(true);

      // Clear input immediately
      setInputValue('');

      // Connect SSE for real-time updates BEFORE sending message
      await sseService.connect(taskId, {
        onMessage: (event: any) => {
          console.log('SSE message received:', event);
          handleRealTimeEvent(event as RealTimeEvent);
        },
        onError: (error) => {
          console.error('SSE error:', error);
        }
      });

      // Subscribe to WebSocket updates
      if (websocketService.isConnected()) {
        websocketService.subscribeToTask(taskId);
      }

      // Send to backend AFTER establishing connections
      await agentAPI.postMessage(taskId, { text: content });

      // Refresh task list after a short delay to get updated title
      // The backend updates the title when the first message is sent
      if (onTaskUpdate) {
        setTimeout(() => {
          onTaskUpdate();
        }, 500); // Small delay to allow backend to process
      }

    } catch (err) {
      setError('Failed to send message');
      console.error('Error sending message:', err);
      setAgentRunning(false);
    } finally {
      setLoading(false);
    }
  }, [taskId, loading]);

  // Stop agent
  const stopAgent = useCallback(async () => {
    if (!taskId) return;

    try {
      console.log('Attempting to stop agent for task:', taskId);
      await agentAPI.stop(taskId);
      setAgentRunning(false);
      console.log('Stop signal sent to agent');
    } catch (err) {
      console.error('Error stopping agent:', err);
      // Even if stop fails, set agent as not running
      setAgentRunning(false);
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
        console.log('Event content:', event.content);
        
        // Preserve original content structure if it's an object/array, otherwise extract text
        let messageContent: any;
        if (typeof event.content === 'object' && event.content !== null) {
          // Check if it's a tool_use block directly
          if (event.content.type === 'tool_use') {
            messageContent = event.content;
          }
          // Check if it's wrapped in {"text": ...}
          else if (event.content.text !== undefined) {
            messageContent = event.content.text;
          }
          // Otherwise preserve the structure
          else {
            messageContent = event.content;
          }
        } else {
          messageContent = extractTextContent(event.content);
        }
        
        const message: ChatMessage = {
          id: Date.now().toString(),
          type: event.role === 'user' ? 'user' : 'assistant',
          content: messageContent,
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
        
        // If this is an assistant message, the agent is running
        if (event.role === 'assistant') {
          setAgentRunning(true);
        }
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
        setAgentRunning(true);
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
        setAgentRunning(true);
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
        setAgentRunning(true);
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
        setAgentRunning(false);
        break;

      case 'completion':
        // Agent has completed successfully
        setAgentRunning(false);
        break;

      default:
        console.log('Unknown event type:', event.type);
    }
  }, []);

  // Cleanup SSE connection on unmount
  useEffect(() => {
    return () => {
      if (taskId) {
        sseService.disconnectTask(taskId);
      }
    };
  }, []);

  return {
    messages,
    inputValue,
    setInputValue,
    sendMessage,
    stopAgent,
    loading,
    error,
    agentRunning,
    refreshMessages: () => {
      // Trigger reload of messages
      if (taskId) {
        const loadMessages = async () => {
          try {
            const backendMessages = await messageAPI.getByTask(taskId);
            const chatMessages = backendMessages.map(convertBackendMessage);
            setMessages(chatMessages);
          } catch (err) {
            console.error('Error refreshing messages:', err);
          }
        };
        loadMessages();
      }
    }
  };
};