#!/bin/bash
echo "Starting noVNC..."

# Start noVNC with explicit websocket settings
/opt/noVNC/utils/novnc_proxy \
    --vnc localhost:5900 \
    --listen 6080 \
    --web /opt/noVNC \
    > /tmp/novnc.log 2>&1 &

NOVNC_PID=$!

# Wait for noVNC to start
timeout=10
while [ $timeout -gt 0 ]; do
    if netstat -tuln | grep -q ":6080 "; then
        break
    fi
    sleep 1
    ((timeout--))
done

if [ $timeout -eq 0 ]; then
    echo "noVNC failed to start" >&2
    exit 1
fi

echo "noVNC started successfully on port 6080"
echo "noVNC PID: $NOVNC_PID"

# Keep the script running
wait 