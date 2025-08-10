#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

USE_VENV=1
if ! python3 -m venv backend/.venv 2>/dev/null; then
  echo "venv not available; falling back to system install with --break-system-packages"
  USE_VENV=0
fi

if [ "$USE_VENV" = "1" ]; then
  source backend/.venv/bin/activate
fi

# Install backend requirements
if [ -f backend/requirements.txt ]; then
  if [ "$USE_VENV" = "1" ]; then
    pip install --upgrade pip
    pip install -r backend/requirements.txt
  else
    pip3 install --break-system-packages --upgrade pip
    pip3 install --break-system-packages -r backend/requirements.txt
  fi
fi

# Launch backend
if [ "$USE_VENV" = "1" ]; then
  uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
else
  python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
fi
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"

# Launch frontend
pushd frontend >/dev/null
if [ -f package.json ]; then
  npm install --no-audit --no-fund
  npm run dev -- --host 0.0.0.0 --port 5173
else
  echo "No frontend found. Exiting..."
fi
popd >/dev/null