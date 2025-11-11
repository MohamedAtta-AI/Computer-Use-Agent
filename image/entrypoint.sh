#!/bin/bash
set -e

# Change to home directory where scripts are located
cd "$HOME"

export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"
eval "$(pyenv init -)"

./start_all.sh
./novnc_startup.sh

python http_server.py > /tmp/server_logs.txt 2>&1 &

uvicorn backend.main:app --host 0.0.0.0 --port 8000

echo "✨ Computer Use Demo is ready!"
echo "➡️  Open http://localhost:8000 in your browser to begin"

# Keep the container running
tail -f /dev/null
