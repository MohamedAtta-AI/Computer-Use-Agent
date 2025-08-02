#!/usr/bin/env bash
set -euo pipefail

# Initialize pyenv environment
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
export PATH="$HOME/.pyenv/shims:$HOME/.pyenv/bin:$PATH"

# 1 – bring up the virtual desktop + VNC stack
./start_all.sh          # Xvfb + window-manager + tint2
./novnc_startup.sh      # noVNC on :6080

# 2 – start the FastAPI backend that ALSO serves the React SPA (dist/ folder)
# Adjust the module path if you renamed `app/main.py`.
echo "🛰  Launching backend on :8000 …"
python -m uvicorn backend.app.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --proxy-headers \
        --forwarded-allow-ips='*' \
        > /tmp/uvicorn.log 2>&1 &

echo
echo "➡️  Open  http://localhost:8000  in your browser."

# 3 – keep container alive
tail -f /dev/null
