#!/usr/bin/env python3
"""
Windows VNC Setup Script
This script sets up TightVNC for Windows users
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

def find_tightvnc():
    """Find TightVNC installation."""
    possible_paths = [
        "C:/Program Files/TightVNC/tvnserver.exe",
        "C:/Program Files (x86)/TightVNC/tvnserver.exe",
        "tvnserver.exe"  # If in PATH
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def install_tightvnc():
    """Install TightVNC if not found."""
    print("TightVNC not found. Installing...")
    
    # Create VNC directory
    vnc_dir = Path("C:/VNC")
    vnc_dir.mkdir(exist_ok=True)
    
    # Download TightVNC
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
    tvnserver_path = find_tightvnc()
    
    if not tvnserver_path:
        print("TightVNC not found. Please install it first.")
        return None
    
    print(f"Starting VNC server on port {port}...")
    
    try:
        cmd = f'"{tvnserver_path}" -port {port} -geometry 1920x1080 -depth 24'
        
        # Start in background
        process = subprocess.Popen(
            cmd,
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
    print("=== Windows VNC Setup for Computer Use Agent ===")
    print()
    
    if platform.system() != "Windows":
        print("This script is designed for Windows.")
        return
    
    # Check if TightVNC is installed
    tvnserver_path = find_tightvnc()
    if not tvnserver_path:
        print("TightVNC not found. Installing...")
        if not install_tightvnc():
            print("Failed to install TightVNC. Please install manually.")
            return
        tvnserver_path = find_tightvnc()
    
    print(f"TightVNC found at: {tvnserver_path}")
    
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