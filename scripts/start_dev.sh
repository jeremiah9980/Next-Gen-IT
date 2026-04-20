#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Starting backend on http://localhost:8000"
(
  cd "$ROOT_DIR/backend"
  python -m uvicorn app.main:app --reload --port 8000
) &

BACKEND_PID=$!

echo "Starting frontend on http://localhost:4173"
(
  cd "$ROOT_DIR/frontend"
  python -m http.server 4173
) &

FRONTEND_PID=$!

trap 'kill $BACKEND_PID $FRONTEND_PID' EXIT
wait
