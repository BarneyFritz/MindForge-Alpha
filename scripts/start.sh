#!/usr/bin/env bash
set -euo pipefail

# Ensure directories
mkdir -p /workspace/data/exports

# Backend deps (user install due to managed env)
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
python3 -m pip install --user -r /workspace/backend/requirements.txt --no-cache-dir --break-system-packages | cat

# Frontend
if [ ! -d "/workspace/frontend/node_modules" ]; then
  cd /workspace/frontend && npm i
fi

# Start backend
(python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000) &
BACK_PID=$!

# Start frontend (foreground)
cd /workspace/frontend
npm run dev -- --host 0.0.0.0 --port 5173

# Cleanup on exit
kill $BACK_PID || true