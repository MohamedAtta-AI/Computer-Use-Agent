#!/bin/bash
set -e

echo "Starting Xvfb..."
Xvfb :1 -screen 0 ${WIDTH}x${HEIGHT}x24 > /tmp/xvfb.log 2>&1 &
XVFB_PID=$!

# Wait for Xvfb to start
sleep 2

echo "Starting window manager..."
mutter --display=:1 --no-x11 --sm-disable --replace > /tmp/mutter.log 2>&1 &
MUTTER_PID=$!

sleep 2

echo "Starting x11vnc..."
x11vnc -display :1 \
    -forever \
    -shared \
    -wait 50 \
    -rfbport 5900 \
    -nopw \
    > /tmp/x11vnc.log 2>&1 &

X11VNC_PID=$!

# Wait for x11vnc to start
timeout=10
while [ $timeout -gt 0 ]; do
    if netstat -tuln | grep -q ":5900 "; then
        break
    fi
    sleep 1
    ((timeout--))
done

if [ $timeout -eq 0 ]; then
    echo "x11vnc failed to start" >&2
    exit 1
fi

echo "VNC server started successfully on port 5900"
echo "Xvfb PID: $XVFB_PID"
echo "Mutter PID: $MUTTER_PID"
echo "x11vnc PID: $X11VNC_PID"

# Keep the script running
wait 