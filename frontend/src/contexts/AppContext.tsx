import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { apiService, Session, Message } from "@/lib/api";
import { toast } from "sonner";

interface AppContextType {
  currentSession: Session | null;
  sessions: Session[];
  messages: Message[];
  isLoading: boolean;
  ws: WebSocket | null;
  createSession: (title: string, description?: string) => Promise<void>;
  selectSession: (session: Session) => Promise<void>;
  sendMessage: (message: string) => Promise<void>;
  loadSessions: () => Promise<void>;
  loadMessages: (sessionId: number) => Promise<void>;
  connectWebSocket: (sessionId: number) => void;
  disconnectWebSocket: () => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error("useApp must be used within an AppProvider");
  }
  return context;
};

interface AppProviderProps {
  children: ReactNode;
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  const [currentSession, setCurrentSession] = useState<Session | null>(null);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);

  const createSession = async (title: string, description?: string) => {
    try {
      setIsLoading(true);
      const session = await apiService.createSession({
        title,
        description,
        model_name: "claude-sonnet-4-20250514",
        max_tokens: 4096,
        temperature: 1.0,
      });
      
      setCurrentSession(session);
      setSessions(prev => [session, ...prev]);
      connectWebSocket(session.id);
      toast.success("New session created successfully");
    } catch (error) {
      toast.error("Failed to create session");
      console.error("Error creating session:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const selectSession = async (session: Session) => {
    try {
      setIsLoading(true);
      setCurrentSession(session);
      await loadMessages(session.id);
      connectWebSocket(session.id);
      toast.success(`Switched to session: ${session.title}`);
    } catch (error) {
      toast.error("Failed to select session");
      console.error("Error selecting session:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async (message: string) => {
    if (!currentSession) {
      await createSession("New Chat Session");
      return;
    }

    try {
      // Add user message to UI immediately
      const userMessage: Message = {
        id: Date.now(),
        session_id: currentSession.id,
        role: "user",
        message_type: "text",
        content: message,
        created_at: new Date().toISOString(),
      };
      setMessages(prev => [...prev, userMessage]);

      // Send via WebSocket if connected
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
          type: "chat",
          data: { message }
        }));
      } else {
        // Fallback to HTTP API
        const response = await apiService.sendMessage({
          session_id: currentSession.id,
          message
        });
        
        const aiMessage: Message = {
          id: response.message_id,
          session_id: currentSession.id,
          role: "assistant",
          message_type: response.message_type,
          content: response.content,
          created_at: response.created_at,
        };
        setMessages(prev => [...prev, aiMessage]);
      }
    } catch (error) {
      toast.error("Failed to send message");
      console.error("Error sending message:", error);
    }
  };

  const loadSessions = async () => {
    try {
      setIsLoading(true);
      const response = await apiService.getSessions();
      setSessions(response.sessions);
    } catch (error) {
      toast.error("Failed to load sessions");
      console.error("Error loading sessions:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadMessages = async (sessionId: number) => {
    try {
      const messages = await apiService.getMessages(sessionId);
      // Convert ChatResponse to Message format
      const convertedMessages: Message[] = messages.map(msg => ({
        id: msg.message_id,
        session_id: sessionId,
        role: msg.role,
        message_type: msg.message_type,
        content: msg.content,
        created_at: msg.created_at,
      }));
      setMessages(convertedMessages);
    } catch (error) {
      toast.error("Failed to load messages");
      console.error("Error loading messages:", error);
    }
  };

  const connectWebSocket = (sessionId: number) => {
    if (ws) {
      ws.close();
    }

    const websocket = apiService.createWebSocketConnection(sessionId);
    
    websocket.onopen = () => {
      console.log("WebSocket connected");
      toast.success("Connected to session");
    };

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case "assistant_message":
          const aiMessage: Message = {
            id: data.data.message_id,
            session_id: sessionId,
            role: "assistant",
            message_type: data.data.message_type,
            content: data.data.content,
            created_at: data.data.created_at,
          };
          setMessages(prev => [...prev, aiMessage]);
          break;
        case "progress":
          console.log("Progress:", data.data);
          break;
        case "error":
          toast.error(`Error: ${data.data.error}`);
          break;
      }
    };

    websocket.onclose = () => {
      console.log("WebSocket disconnected");
    };

    websocket.onerror = (error) => {
      console.error("WebSocket error:", error);
      toast.error("WebSocket connection error");
    };

    setWs(websocket);
  };

  const disconnectWebSocket = () => {
    if (ws) {
      ws.close();
      setWs(null);
    }
  };

  useEffect(() => {
    loadSessions();
  }, []);

  useEffect(() => {
    return () => {
      disconnectWebSocket();
    };
  }, []);

  const value: AppContextType = {
    currentSession,
    sessions,
    messages,
    isLoading,
    ws,
    createSession,
    selectSession,
    sendMessage,
    loadSessions,
    loadMessages,
    connectWebSocket,
    disconnectWebSocket,
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};
