#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
(cd backend && exec .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000) &
backend_pid=$!
(cd frontend && exec npm run dev) &
frontend_pid=$!
trap 'kill "$backend_pid" "$frontend_pid" 2>/dev/null || true' EXIT INT TERM
wait
