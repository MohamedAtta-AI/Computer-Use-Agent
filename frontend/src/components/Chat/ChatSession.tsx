import React, { useRef, useEffect } from "react";
import { ChatMessage } from "./ChatMessage";
import { ChatMessage as ChatMessageType } from "../../types";
import { Send, MessageSquare, Square } from "lucide-react";

interface ChatSessionProps {
  messages: ChatMessageType[];
  inputValue: string;
  onInputChange: (value: string) => void;
  onSendMessage: (message: string) => void;
  onStopAgent?: () => void;
  loading?: boolean;
  error?: string | null;
  selectedTaskId?: string | null;
  agentRunning?: boolean;
}

export const ChatSession: React.FC<ChatSessionProps> = ({
  messages,
  inputValue,
  onInputChange,
  onSendMessage,
  onStopAgent,
  loading = false,
  error = null,
  selectedTaskId = null,
  agentRunning = false,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, loading, agentRunning]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim() && !loading && !agentRunning) {
      onSendMessage(inputValue);
    }
  };

  const handleStopAgent = () => {
    if (onStopAgent) {
      onStopAgent();
    }
  };

  return (
    <div className="flex flex-col flex-1 min-h-0">
      <div className="flex items-center space-x-2 p-3 border-b border-gray-200">
        <MessageSquare className="w-4 h-4 text-gray-500" />
        <h3 className="text-sm font-medium text-gray-700">Chat Session</h3>
        {selectedTaskId && (
          <span className="text-xs text-gray-500">
            Task: {selectedTaskId.slice(0, 8)}...
          </span>
        )}
        {agentRunning && (
          <span className="text-xs text-blue-600 font-medium">
            Agent Running
          </span>
        )}
      </div>

      {error && (
        <div className="p-2 bg-red-50 border-b border-red-200">
          <p className="text-xs text-red-600">{error}</p>
        </div>
      )}

      <div
        ref={messagesContainerRef}
        className="flex-1 overflow-y-auto p-3 space-y-2"
      >
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}
        {loading && (
          <div className="text-sm text-gray-500 italic">Loading...</div>
        )}
        {agentRunning && (
          <div className="text-sm text-blue-500 italic">
            Agent is working...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="p-3 border-t border-gray-200">
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => onInputChange(e.target.value)}
            placeholder={
              agentRunning ? "Agent is running..." : "Type your message..."
            }
            disabled={loading || !selectedTaskId || agentRunning}
            className="flex-1 px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
          />
          {agentRunning ? (
            <button
              type="button"
              onClick={handleStopAgent}
              className="px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700 transition-colors"
              title="Stop Agent"
            >
              <Square className="w-4 h-4" />
            </button>
          ) : (
            <button
              type="submit"
              disabled={!inputValue.trim() || loading || !selectedTaskId}
              className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          )}
        </div>
      </form>
    </div>
  );
};
