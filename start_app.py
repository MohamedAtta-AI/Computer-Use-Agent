#!/usr/bin/env python3
"""
Simple script to start the Computer Use Agent application
"""

import os
import sys
import subprocess
import platform
import time
from pathlib import Path

def check_port(port):
    """Check if a port is in use."""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def start_vnc_server():
    """Start VNC server based on platform."""
    if platform.system() == "Windows":
        # Try to find and start TightVNC
        possible_paths = [
            "C:/Program Files/TightVNC/tvnserver.exe",
            "C:/Program Files (x86)/TightVNC/tvnserver.exe",
            "tvnserver.exe"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"Starting TightVNC from: {path}")
                subprocess.Popen([path, "-port", "5900"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE)
                return True
        
        print("TightVNC not found. Please install it from: https://www.tightvnc.com/download.php")
        return False
    else:
        # For Linux/Mac, try to start x11vnc
        try:
            subprocess.Popen(["x11vnc", "-display", ":0", "-port", "5900", "-forever", "-shared"],
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE)
            return True
        except FileNotFoundError:
            print("x11vnc not found. Please install it or use Docker setup.")
            return False

def main():
    print("🚀 Starting Computer Use Agent...")
    print()
    
    # Check if backend is already running
    if check_port(8000):
        print("✅ Backend already running on port 8000")
    else:
        print("📡 Starting backend...")
        backend_dir = Path("backend")
        if backend_dir.exists():
            original_dir = os.getcwd()
            os.chdir(backend_dir)
            subprocess.Popen([sys.executable, "run.py"], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE)
            os.chdir(original_dir)  # Return to original directory
            print("✅ Backend started")
        else:
            print("❌ Backend directory not found")
            return
    
    # Check if VNC is running
    if check_port(5900):
        print("✅ VNC server already running on port 5900")
    else:
        print("🖥️  Starting VNC server...")
        if start_vnc_server():
            print("✅ VNC server started")
        else:
            print("⚠️  VNC server not started. You may need to start it manually.")
    
    # Check if frontend is running
    if check_port(8080):
        print("✅ Frontend already running on port 8080")
    else:
        print("🌐 Starting frontend...")
        frontend_dir = Path("frontend")
        print(f"Looking for frontend directory at: {frontend_dir.absolute()}")
        if frontend_dir.exists():
            print(f"✅ Found frontend directory")
            # Check if npm is available
            try:
                subprocess.run(["npm", "--version"], capture_output=True, check=True)
                print("✅ npm found")
                os.chdir(frontend_dir)
                print(f"Changed to directory: {os.getcwd()}")
                
                # Check if node_modules exists, if not install dependencies
                if not Path("node_modules").exists():
                    print("📦 Installing frontend dependencies...")
                    subprocess.run(["npm", "install"], check=True)
                
                subprocess.Popen(["npm", "run", "dev"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE)
                print("✅ Frontend started")
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                print(f"❌ npm not found: {e}")
                print("   Please install Node.js from: https://nodejs.org/")
                print("   Or start the frontend manually:")
                print("   cd frontend && npm install && npm run dev")
        else:
            print(f"❌ Frontend directory not found at: {frontend_dir.absolute()}")
            print("   Available directories:")
            for item in Path(".").iterdir():
                if item.is_dir():
                    print(f"   - {item.name}")
            return
    
    print()
    print("🎉 Application started successfully!")
    print()
    print("📱 Open your browser to: http://localhost:8080")
    print("🖥️  VNC server: vnc://localhost:5900")
    print("🌐 noVNC (if available): http://localhost:6080")
    print()
    print("💡 Tips:")
    print("  - Create a new session by clicking 'New Agent Task'")
    print("  - Click 'Connect' in the VNC panel")
    print("  - Start chatting with the agent")
    print()
    print("Press Ctrl+C to stop all services")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        print("✅ Services stopped")

if __name__ == "__main__":
    main() 