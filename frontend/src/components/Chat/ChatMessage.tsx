import React from 'react';
import { ChatMessage as ChatMessageType } from '../../types';
import { User, Bot, Code, CheckCircle } from 'lucide-react';

interface ChatMessageProps {
  message: ChatMessageType;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const getMessageConfig = (type: ChatMessageType['type']) => {
    switch (type) {
      case 'user':
        return {
          icon: User,
          bgColor: 'bg-blue-50',
          textColor: 'text-gray-900',
          label: 'User'
        };
      case 'assistant':
        return {
          icon: Bot,
          bgColor: 'bg-gray-50',
          textColor: 'text-gray-900',
          label: 'Assistant'
        };
      case 'function_call':
        return {
          icon: Code,
          bgColor: 'bg-orange-50',
          textColor: 'text-orange-800',
          label: 'Function Call'
        };
      case 'function_result':
        return {
          icon: CheckCircle,
          bgColor: 'bg-green-50',
          textColor: 'text-green-800',
          label: 'Function Result'
        };
      case 'event':
        return {
          icon: Code,
          bgColor: 'bg-purple-50',
          textColor: 'text-purple-800',
          label: 'Event'
        };
      case 'screenshot':
        return {
          icon: CheckCircle,
          bgColor: 'bg-blue-50',
          textColor: 'text-blue-800',
          label: 'Screenshot'
        };
    }
  };

  // Helper function to extract text content from message
  const getMessageText = (content: any): string => {
    if (typeof content === 'string') {
      return content;
    }
    if (typeof content === 'object' && content !== null) {
      if (content.text) {
        return content.text;
      }
      if (content.content) {
        return getMessageText(content.content);
      }
      // If it's an object but no text property, stringify it
      return JSON.stringify(content);
    }
    return String(content);
  };

  const config = getMessageConfig(message.type);
  const Icon = config.icon;
  const messageText = getMessageText(message.content);

  return (
    <div className={`p-3 rounded-lg ${config.bgColor} mb-3`}>
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0">
          <Icon className="w-4 h-4 text-gray-500 mt-1" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs font-medium text-gray-600">{config.label}</span>
            <span className="text-xs text-gray-400">{message.timestamp}</span>
          </div>
          <div className={`text-sm ${config.textColor}`}>
            {message.type === 'function_call' ? (
              <code className="font-mono bg-orange-100 px-1 py-0.5 rounded">
                {message.functionName}
                {messageText}
              </code>
            ) : message.type === 'screenshot' && message.url ? (
              <div>
                <p>{messageText}</p>
                <img 
                  src={`http://localhost:8000${message.url}`} 
                  alt="Screenshot" 
                  className="mt-2 max-w-full h-auto rounded border"
                  style={{ maxHeight: '200px' }}
                />
              </div>
            ) : (
              <p>{messageText}</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};