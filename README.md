# Computer Use Agent

A scalable backend for computer use agent session management with real-time VNC integration.

## 🚀 Quick Start

### Option 1: Simple Start Script (Recommended)
```bash
python start_app.py
```

This will automatically start:
- Backend (FastAPI) on port 8000
- VNC server on port 5900  
- Frontend (React) on port 8080

### Option 2: Docker with Full VNC Environment
```bash
cd backend
docker-compose -f docker-compose.vnc.yml up --build
```

### Option 3: Manual Setup
1. **Start VNC Server:**
   ```bash
   # Windows
   tvnserver.exe -port 5900
   
   # Linux/Mac
   x11vnc -display :0 -port 5900 -forever -shared
   ```

2. **Start Backend:**
   ```bash
   cd backend
   python run.py
   ```

3. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the `backend` directory:

```env
# Database Configuration
DATABASE_URL=sqlite:///./computer_use_agent.db

# Anthropic API Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Security Configuration
SECRET_KEY=your_secret_key_here_make_it_long_and_random

# File Upload Configuration
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=104857600

# VNC Configuration
VNC_HOST=localhost
VNC_PORT=5900

# Server Configuration
DEBUG=true
HOST=0.0.0.0
PORT=8000
```

## 🎯 How to Use

1. **Open your browser** to `http://localhost:8080`
2. **Create a new session** by clicking "New Agent Task"
3. **Click "Connect"** in the VNC panel
4. **Start chatting** - the agent will control the virtual machine

## 🐛 Troubleshooting

### VNC Not Connecting
- Make sure VNC server is running on port 5900
- Check firewall settings
- Try connecting directly: `vnc://localhost:5900`

### "Computer Use Error"
- This happens when the agent tries to use computer tools
- Make sure you have a VNC server running
- The agent needs a virtual machine to control

### Frontend Issues
- Clear browser cache
- Check browser console for errors
- Make sure backend is running on port 8000

### Session Management Issues
- Sessions should now be selectable in the left sidebar
- Click on any session to switch to it
- The current session is highlighted

## 📁 Project Structure

```
Computer-Use-Agent/
├── backend/                 # FastAPI backend
│   ├── app/                # Application code
│   │   ├── api/           # API routes
│   │   ├── services/      # Business logic
│   │   ├── models/        # Database models
│   │   └── core/          # Agent core logic
│   ├── docker-compose.vnc.yml  # Docker setup with VNC
│   └── setup_vnc_windows.py    # Windows VNC setup
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── contexts/      # React contexts
│   │   └── lib/           # Utilities
│   └── package.json
├── computer-use-demo/      # Original working demo
├── start_app.py           # Simple startup script
└── VNC_SETUP_GUIDE.md     # Detailed VNC setup guide
```

## 🔗 Ports Used

- **8000**: FastAPI backend
- **5900**: VNC server
- **6080**: noVNC web interface (Docker only)
- **8080**: React frontend

## 🛠️ Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
python run.py
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Database Migrations
```bash
cd backend
alembic upgrade head
```

## 📚 Features

- ✅ **Session Management** - Create and manage chat sessions
- ✅ **Real-time Chat** - WebSocket-based real-time messaging
- ✅ **VNC Integration** - Virtual machine control via VNC
- ✅ **File Management** - Upload and manage files
- ✅ **Agent Tools** - Computer use tools for automation
- ✅ **Database Persistence** - SQLite/PostgreSQL support
- ✅ **Docker Support** - Containerized deployment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.