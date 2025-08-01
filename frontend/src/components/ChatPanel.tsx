import { Send, Mic, Square, Bot, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { useApp } from "@/contexts/AppContext";
import { useState, useRef, useEffect } from "react";

const ChatPanel = () => {
  const { messages, sendMessage, currentSession, ws } = useApp();
  const [inputMessage, setInputMessage] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;
    
    const message = inputMessage.trim();
    setInputMessage("");
    await sendMessage(message);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleRecording = () => {
    setIsRecording(!isRecording);
    // TODO: Implement actual recording functionality
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: "2-digit", 
      minute: "2-digit" 
    });
  };

  return (
    <div className="h-full bg-chat-bg border-l border-border flex flex-col">
      {/* Chat Header */}
      <div className="p-4 border-b border-border flex-shrink-0">
        <div className="flex items-center gap-3 mb-4">
          <Button 
            variant={isRecording ? "destructive" : "default"} 
            size="sm" 
            className="flex items-center gap-2"
            onClick={handleRecording}
          >
            <Mic className="h-4 w-4" />
            {isRecording ? "Recording..." : "Record"}
          </Button>
          <Button 
            variant="secondary" 
            size="sm" 
            className="flex items-center gap-2"
            onClick={() => setIsRecording(false)}
          >
            <Square className="h-4 w-4" />
            Stop
          </Button>
        </div>
        
        {/* Connection Status */}
        <div className="flex items-center gap-2 text-sm">
          <div className={`w-2 h-2 rounded-full ${ws?.readyState === WebSocket.OPEN ? "bg-green-500" : "bg-red-500"}`} />
          <span className="text-muted-foreground">
            {ws?.readyState === WebSocket.OPEN ? "Connected" : "Disconnected"}
          </span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 p-4 space-y-4 overflow-y-auto min-h-0">
        {messages.length === 0 ? (
          <div className="flex gap-3">
            <Avatar className="w-8 h-8">
              <AvatarFallback className="bg-primary text-primary-foreground">
                <Bot className="h-4 w-4" />
              </AvatarFallback>
            </Avatar>
            <div className="flex-1">
              <Card className="p-3">
                <p className="text-sm text-foreground">Hi! Let me know what task to accomplish</p>
              </Card>
              <span className="text-xs text-muted-foreground mt-1 block">
                {formatTime(new Date().toISOString())}
              </span>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div key={message.id} className="flex gap-3">
              <Avatar className="w-8 h-8">
                <AvatarFallback className={message.role === "user" ? "bg-blue-500 text-white" : "bg-primary text-primary-foreground"}>
                  {message.role === "user" ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <Card className="p-3">
                  <p className="text-sm text-foreground">{message.content}</p>
                </Card>
                <span className="text-xs text-muted-foreground mt-1 block">
                  {formatTime(message.created_at)}
                </span>
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Chat Input */}
      <div className="p-4 border-t border-border">
        <div className="flex gap-2">
          <Input 
            placeholder="Write a message" 
            className="flex-1"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={!currentSession}
          />
          <Button 
            size="icon" 
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || !currentSession}
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ChatPanel;
