#!/bin/bash

echo "Starting Urban Mobility Data Living Laboratory (UMDL2)..."
echo "========================================================"

echo "Starting backend server..."
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!

echo "Backend server starting on http://localhost:8001"

sleep 3

cd ..

echo "Starting frontend development server..."
npm run dev &
FRONTEND_PID=$!

echo "Frontend server starting on http://localhost:5173"

echo ""
echo "========================================================"
echo "UMDL2 servers are running!"
echo "Frontend: http://localhost:5173"
echo "Backend API: http://localhost:8001"
echo "Backend Docs: http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
echo "========================================================"

trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT

wait