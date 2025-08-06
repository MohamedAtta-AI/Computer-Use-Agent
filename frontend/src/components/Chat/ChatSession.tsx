import React from 'react';
import { ChatMessage } from './ChatMessage';
import { ChatMessage as ChatMessageType } from '../../types';
import { Send, MessageSquare } from 'lucide-react';

interface ChatSessionProps {
  messages: ChatMessageType[];
  inputValue: string;
  onInputChange: (value: string) => void;
  onSendMessage: (message: string) => void;
  loading?: boolean;
  error?: string | null;
  selectedTaskId?: string | null;
}

export const ChatSession: React.FC<ChatSessionProps> = ({
  messages,
  inputValue,
  onInputChange,
  onSendMessage,
  loading = false,
  error = null,
  selectedTaskId = null
}) => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim() && !loading) {
      onSendMessage(inputValue);
    }
  };

  return (
    <div className="flex flex-col h-96">
      <div className="flex items-center space-x-2 p-3 border-b border-gray-200">
        <MessageSquare className="w-4 h-4 text-gray-500" />
        <h3 className="text-sm font-medium text-gray-700">Chat Session</h3>
        {selectedTaskId && (
          <span className="text-xs text-gray-500">Task: {selectedTaskId.slice(0, 8)}...</span>
        )}
      </div>
      
      {error && (
        <div className="p-2 bg-red-50 border-b border-red-200">
          <p className="text-xs text-red-600">{error}</p>
        </div>
      )}
      
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}
        {loading && (
          <div className="text-sm text-gray-500 italic">Loading...</div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="p-3 border-t border-gray-200">
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => onInputChange(e.target.value)}
            placeholder="Type your message..."
            disabled={loading || !selectedTaskId}
            className="flex-1 px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!inputValue.trim() || loading || !selectedTaskId}
            className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  );
};