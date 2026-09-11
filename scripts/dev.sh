#!/usr/bin/env bash
# PorchLight dev launcher: backend on :8000, dashboard on :5173
set -euo pipefail
cd "$(dirname "$0")/.."

echo "🏮 starting backend (http://127.0.0.1:8000/docs) ..."
(cd backend && uv run uvicorn app.main:app --reload) &
BACK_PID=$!

echo "🏮 starting frontend (http://127.0.0.1:5173) ..."
(cd frontend && npm run dev) &
FRONT_PID=$!

trap 'kill $BACK_PID $FRONT_PID 2>/dev/null' EXIT
wait
