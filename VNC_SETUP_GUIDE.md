# VNC Setup Guide

## 🚀 Quick Start (Recommended)

### Option 1: Docker with Full VNC Environment
```bash
cd backend
docker-compose -f docker-compose.vnc.yml up --build
```

This will start:
- FastAPI backend on port 8000
- VNC server on port 5900
- noVNC web interface on port 6080
- Frontend on port 8080

### Option 2: Windows (TightVNC)
```bash
cd backend
python setup_vnc_windows.py
```

### Option 3: Manual Setup
1. Install TightVNC: https://www.tightvnc.com/download.php
2. Start VNC server: `tvnserver.exe -port 5900`
3. Start the backend: `python run.py`
4. Start the frontend: `npm run dev`

## 🔧 How to Use

1. **Start the application** (choose one option above)
2. **Open your browser** to `http://localhost:8080`
3. **Create a new session** by clicking "New Agent Task"
4. **Click "Connect"** in the VNC panel
5. **Start chatting** - the agent will control the virtual machine

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

## 📁 File Structure
```
Computer-Use-Agent/
├── backend/                 # FastAPI backend
│   ├── app/                # Application code
│   ├── docker-compose.vnc.yml  # Docker setup with VNC
│   └── setup_vnc_windows.py    # Windows VNC setup
├── frontend/               # React frontend
└── computer-use-demo/      # Original working demo
```

## 🔗 Ports Used
- **8000**: FastAPI backend
- **5900**: VNC server
- **6080**: noVNC web interface
- **8080**: React frontend

## 💡 Tips
- The VNC display shows a virtual Linux desktop
- You can install software, browse the web, etc.
- The agent can control everything in the virtual machine
- Use the chat to give the agent tasks to perform 