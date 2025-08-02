# Computer Use Agent
**Author: Mohamed Atta**  
A scalable backend system for computer use agent session management, similar to OpenAI Operator. This project provides a FastAPI backend with real-time streaming, VNC integration, and a modern React frontend for managing AI-powered computer automation sessions.

## 🚀 Features

- **Session Management**: Create and manage multiple AI agent sessions
- **Real-time Streaming**: Server-Sent Events (SSE) for live progress updates
- **VNC Integration**: Virtual desktop access via noVNC
- **File Management**: Upload, download, and manage files within sessions
- **Modern UI**: React-based frontend with real-time chat interface
- **Docker Deployment**: Complete containerized setup for easy deployment

## 🏗️ Architecture

### Backend (FastAPI)
- **FastAPI**: Modern Python web framework for high-performance APIs
- **Computer Use Demo**: Integration with Anthropic's computer use tools
- **SQLite Database**: Session and message persistence
- **VNC Server**: Virtual desktop environment with noVNC
- **Real-time Streaming**: SSE for live message updates

### Frontend (React + TypeScript)
- **React 18**: Modern UI framework with hooks
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **Shadcn/ui**: High-quality UI components
- **React Query**: Server state management

### Infrastructure
- **Docker**: Containerized deployment
- **Nginx**: Static file serving and API proxying
- **Xvfb**: Virtual framebuffer for headless desktop
- **tint2**: Lightweight window manager

## 🏗️ Project Structure

```
Computer-Use-Agent/
├── backend/                    # FastAPI backend
│   ├── app/                   # Application code
│   │   ├── main.py           # FastAPI app and routes
│   │   ├── compute_runner.py # Computer use session runner
│   │   ├── db.py             # Database models and setup
│   │   ├── schemas.py        # Pydantic schemas
│   │   └── computer_use_demo/ # Anthropic computer use tools
│   ├── image/                # VNC and desktop setup
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile           # Backend container
├── frontend/                  # React frontend
│   ├── src/                  # Source code
│   │   ├── components/       # React components
│   │   ├── pages/           # Page components
│   │   ├── lib/             # Utilities and API client
│   │   └── App.tsx          # Main app component
│   ├── package.json         # Node.js dependencies
│   └── Dockerfile           # Frontend container
├── docker-compose.yml        # Service orchestration
├── .env                      # Environment variables
└── README.md                # This file
```

## 📋 Prerequisites

- Docker and Docker Compose
- Anthropic API key (for AI functionality)
- At least 4GB RAM (for VNC and desktop environment)

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Computer-Use-Agent
```

### 2. Environment Configuration
Create a `.env` file in the root directory:
```bash
# Required: Your Anthropic API key
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: Claude model (default: claude-sonnet-4-20250514)
CLAUDE_MODEL=claude-sonnet-4-20250514

# Optional: Display configuration
DISPLAY_NUM=1
WIDTH=1280
HEIGHT=768
```

### 3. Build and Start Services
```bash
# Build all containers
docker-compose build --no-cache

# Start all services
docker-compose up -d

# Monitor logs
docker-compose logs -f
```

### 4. Access the Application
- **Frontend**: http://localhost:80
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Direct VNC**: http://localhost:6080

## 🔧 Development Setup

### Backend Development
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 📡 API Endpoints

### Session Management
- `POST /api/sessions` - Create a new session
- `GET /api/sessions` - List all sessions with message counts

### Messaging
- `POST /api/sessions/{session_id}/messages` - Send a message to a session
- `GET /api/sessions/{session_id}/stream` - Stream real-time messages (SSE)

### File Management
- `POST /api/files/upload` - Upload a file to a session
- `GET /api/files/{file_id}` - Download a file
- `GET /api/files?session_id={session_id}` - List files in a session
- `DELETE /api/files/{file_id}` - Delete a file

### Health & Status
- `GET /api/healthz` - Health check endpoint

### VNC
- `WS /api/vnc` - WebSocket endpoint for VNC connection

## 🎯 Usage

### 1. Starting a New Session
1. Open the application at http://localhost:80
2. The system automatically creates a new session
3. You'll see the chat interface and VNC panel

### 2. Interacting with the AI Agent
1. Type your request in the chat input
2. The AI agent will process your request and respond
3. Real-time updates appear in the chat stream
4. The agent can perform computer tasks in the virtual desktop

### 3. File Management
1. Use the file panel to upload files
2. Files are associated with the current session
3. Download or delete files as needed

### 4. VNC Desktop Access
1. The VNC panel shows the virtual desktop
2. The AI agent can interact with the desktop environment
3. You can also connect directly via http://localhost:6080

## 🔒 Security Considerations

- **API Keys**: Store sensitive keys in environment variables
- **File Uploads**: Implement file type and size validation
- **VNC Access**: Consider authentication for VNC connections
- **Database**: Use proper database security in production

## 🚀 Production Deployment

### Environment Variables
```bash
# Production environment variables
ANTHROPIC_API_KEY=your_production_key
CLAUDE_MODEL=claude-sonnet-4-20250514
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port
```

### Reverse Proxy Setup
```nginx
# Example Nginx configuration
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://frontend:80;
    }
    
    location /api/ {
        proxy_pass http://backend:8000;
    }
    
    location /vnc/ {
        proxy_pass http://backend:6080;
    }
}
```

### Database Migration
For production, consider migrating from SQLite to PostgreSQL:
```bash
# Update docker-compose.yml with PostgreSQL service
# Update backend configuration for PostgreSQL
# Run database migrations
```
---

**Note**: This project is designed for development and testing. For production use, implement proper security measures, monitoring, and scaling strategies. 
