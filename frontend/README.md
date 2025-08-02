# Computer Use Agent Frontend

A modern React-based interface for computer use agents, featuring real-time VNC display, chat sessions, and file management capabilities.

## 🏗️ Architecture Overview

This frontend is designed as a complete UI for computer use agents with three main panels:

- **Left Sidebar**: Task history and new task creation
- **Center Panel**: VNC connection displaying the agent's virtual machine
- **Right Panel**: Split between chat session (top) and file management (bottom)

## 🚀 Features

### Task Management
- **Task History**: View all previous agent tasks with timestamps
- **New Task Creation**: Start new agent tasks with a single click
- **Task Status Tracking**: Visual indicators for task states

### VNC Integration
- **Real-time Display**: Live view of the agent's virtual machine
- **Connection Status**: Visual feedback for VNC connection state
- **Responsive Layout**: Scales to available space

### Chat System
- **Real-time Messaging**: Support for user messages, agent responses, function calls, and results
- **Message Types**: Distinct styling for different message types
- **Auto-scroll**: Automatic scrolling to latest messages
- **Timestamp Display**: Human-readable timestamps for all messages

### File Management
- **Drag & Drop Upload**: Easy file upload interface
- **File Preview**: Support for different file types with appropriate icons
- **Download/Delete**: Actions for managing uploaded files
- **Recent Files**: Quick access to recently uploaded files

## 🛠️ Tech Stack

- **React 18** with TypeScript
- **Tailwind CSS** with custom design system
- **Radix UI** components for accessibility
- **Lucide React** for icons
- **React Router** for navigation
- **Vite** for development and building

## 📦 Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd computer-use-agent-frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## 🔧 Backend Integration

This frontend is designed to be easily integrated with your backend. Here are the key integration points:

### WebSocket Connections

The chat system expects real-time communication. Implement WebSocket handlers for:

```typescript
// Message types the frontend expects
interface Message {
  id: string;
  type: 'user' | 'assistant' | 'function' | 'result';
  content: string;
  timestamp: Date;
}

// WebSocket events to handle
ws.on('message', (message: Message) => {
  // Add to chat history
});

ws.on('task_update', (taskUpdate) => {
  // Update task status
});
```

### VNC Integration

The VNC panel expects a WebSocket connection to a VNC server:

```typescript
// VNC connection configuration
const vncConfig = {
  url: 'ws://your-vnc-server:port',
  // Add authentication if needed
};
```

### File Upload API

The file management system needs these endpoints:

```typescript
// File upload
POST /api/files/upload
Content-Type: multipart/form-data

// File download
GET /api/files/:fileId

// File deletion
DELETE /api/files/:fileId

// List files
GET /api/files
```

### Task Management API

```typescript
// Create new task
POST /api/tasks
{
  description: string;
  parameters?: object;
}

// Get task history
GET /api/tasks

// Get task details
GET /api/tasks/:taskId

// Update task status
PATCH /api/tasks/:taskId
{
  status: 'pending' | 'running' | 'completed' | 'failed';
}
```

## 🎨 Design System

The UI uses a comprehensive design system defined in `src/index.css` and `tailwind.config.ts`:

### Color Tokens
- `--agent-blue`: Primary blue for agent-related elements
- `--vnc-background`: Dark blue for VNC panel background
- `--chat-background`: Light background for chat area
- `--panel-border`: Subtle borders between panels

### Component Customization

All components use semantic color tokens. To customize:

1. Update color values in `src/index.css`
2. Colors automatically support light/dark mode
3. Use HSL format for all colors

## 📁 Project Structure

```
src/
├── components/
│   ├── ui/                 # Reusable UI components (shadcn/ui)
│   ├── ChatPanel.tsx       # Chat interface component
│   ├── FilePanel.tsx       # File management component
│   ├── TaskSidebar.tsx     # Task history sidebar
│   └── VNCPanel.tsx        # VNC display component
├── pages/
│   ├── Index.tsx           # Main application page
│   └── NotFound.tsx        # 404 page
├── lib/
│   └── utils.ts            # Utility functions
├── hooks/                  # Custom React hooks
├── index.css               # Global styles and design system
└── main.tsx               # Application entry point
```

## 🔌 Integration Examples

### Adding Real-time Chat

```typescript
// In your chat component
const [socket, setSocket] = useState<WebSocket | null>(null);

useEffect(() => {
  const ws = new WebSocket('ws://your-backend:port/chat');
  
  ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    setMessages(prev => [...prev, message]);
  };
  
  setSocket(ws);
  
  return () => ws.close();
}, []);

const sendMessage = (content: string) => {
  if (socket) {
    socket.send(JSON.stringify({
      type: 'user',
      content,
      timestamp: new Date()
    }));
  }
};
```

### Adding VNC Connection

```typescript
// Install a VNC client library like @novnc/novnc
import RFB from '@novnc/novnc/core/rfb';

const VNCComponent = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  useEffect(() => {
    if (canvasRef.current) {
      const rfb = new RFB(canvasRef.current, 'ws://vnc-server:port');
      
      rfb.addEventListener('connect', () => {
        console.log('VNC connected');
      });
      
      return () => rfb.disconnect();
    }
  }, []);
  
  return <canvas ref={canvasRef} />;
};
```

### Adding File Upload

```typescript
const handleFileUpload = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await fetch('/api/files/upload', {
      method: 'POST',
      body: formData,
    });
    
    if (response.ok) {
      const result = await response.json();
      // Update file list
      setFiles(prev => [...prev, result]);
    }
  } catch (error) {
    console.error('Upload failed:', error);
  }
};
```

## 🔧 Customization

### Adding New Message Types

To support additional message types in the chat:

1. Update the `Message` interface in `ChatPanel.tsx`
2. Add new styling in the message rendering logic
3. Update the backend to send the new message types

### Styling Modifications

- All colors use CSS custom properties for easy theming
- Components use Tailwind classes with semantic tokens
- Dark mode is automatically supported

### Adding New Panels

To add new panels or modify layout:

1. Create new component in `src/components/`
2. Update the layout in `src/pages/Index.tsx`
3. Add any new color tokens to the design system

## 🤝 Contributing

1. Follow the existing code structure and patterns
2. Use TypeScript for all new components
3. Follow the design system for styling
4. Add proper error handling and loading states
5. Test responsiveness across different screen sizes

## 📄 License

[Add your license information here]

## 🆘 Support

[Add support information or links to documentation]