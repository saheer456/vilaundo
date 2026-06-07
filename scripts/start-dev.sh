#!/usr/bin/env bash
# Start both backend and frontend for local development (bash)
# Usage: ./scripts/start-dev.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export DISABLE_SCHEDULER=1
export VITE_API_URL="http://127.0.0.1:8000"

if [ "${1:-}" != "--no-install" ]; then
  echo "Installing frontend dependencies (npm ci)"
  (cd frontend && npm ci)
fi

echo "Starting backend (uvicorn) on 127.0.0.1:8000"
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000 &
UVICORN_PID=$!

echo "Starting frontend (vite)"
(cd frontend && npm run dev) &
VITE_PID=$!

echo "Backend PID: $UVICORN_PID; Frontend PID: $VITE_PID"
echo "To stop: kill $UVICORN_PID $VITE_PID"

wait
