#!/bin/bash

# Get the directory of this script
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Start backend
cd "$PROJECT_DIR/backend"
echo "Starting backend (FastAPI)..."
uvicorn main:app --reload &
BACKEND_PID=$!

# Start frontend
cd "$PROJECT_DIR/frontend"
echo "Starting frontend (React)..."
npm run dev &
FRONTEND_PID=$!

# Wait for both to exit
wait $BACKEND_PID $FRONTEND_PID 