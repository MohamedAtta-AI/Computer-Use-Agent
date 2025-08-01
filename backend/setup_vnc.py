#!/usr/bin/env python3
"""
VNC Server Setup Script for Windows
This script helps set up a VNC server for the Computer Use Agent
"""

import os
import sys
import subprocess
import platform
import requests
import zipfile
import tempfile
from pathlib import Path

def download_file(url, filename):
    """Download a file from URL."""
    print(f"Downloading {filename}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Downloaded {filename}")

def setup_tightvnc():
    """Set up TightVNC server on Windows."""
    print("Setting up TightVNC server...")
    
    # Create VNC directory
    vnc_dir = Path("C:/VNC")
    vnc_dir.mkdir(exist_ok=True)
    
    # Download TightVNC if not exists
    tightvnc_url = "https://www.tightvnc.com/download/2.8.27/tightvnc-2.8.27-gpl-setup-64bit.msi"
    installer_path = vnc_dir / "tightvnc-setup.msi"
    
    if not installer_path.exists():
        try:
            download_file(tightvnc_url, installer_path)
        except Exception as e:
            print(f"Failed to download TightVNC: {e}")
            print("Please download manually from: https://www.tightvnc.com/download.php")
            return False
    
    # Install TightVNC
    print("Installing TightVNC...")
    try:
        subprocess.run([
            "msiexec", "/i", str(installer_path), 
            "/quiet", "/norestart",
            "ADDLOCAL=Server"
        ], check=True)
        print("TightVNC installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install TightVNC: {e}")
        return False

def start_vnc_server(port=5900):
    """Start VNC server on specified port."""
    print(f"Starting VNC server on port {port}...")
    
    try:
        # Try to start TightVNC server
        cmd = f'tvnserver.exe -port {port} -geometry 1920x1080 -depth 24'
        
        # Start in background
        process = subprocess.Popen(
            cmd.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        
        print(f"VNC server started with PID: {process.pid}")
        print(f"Connect to: localhost:{port}")
        print("Press Ctrl+C to stop the server")
        
        return process
        
    except Exception as e:
        print(f"Failed to start VNC server: {e}")
        return None

def main():
    """Main setup function."""
    print("=== VNC Server Setup for Computer Use Agent ===")
    print()
    
    if platform.system() != "Windows":
        print("This script is designed for Windows. For other platforms:")
        print("- Linux: Install x11vnc or tightvncserver")
        print("- macOS: Install VNC server from System Preferences")
        return
    
    # Check if TightVNC is installed
    try:
        subprocess.run(["tvnserver.exe", "-version"], 
                      capture_output=True, check=True)
        print("TightVNC is already installed!")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("TightVNC not found. Installing...")
        if not setup_tightvnc():
            print("Failed to install TightVNC. Please install manually.")
            return
    
    # Start VNC server
    port = 5900
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number. Using default port 5900.")
    
    process = start_vnc_server(port)
    
    if process:
        try:
            # Keep the server running
            process.wait()
        except KeyboardInterrupt:
            print("\nStopping VNC server...")
            process.terminate()
            process.wait()
            print("VNC server stopped.")

if __name__ == "__main__":
    main() 