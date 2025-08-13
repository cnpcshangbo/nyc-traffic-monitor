#!/bin/bash

# Docker Compose Startup Script for UMDL2
# This script ensures Docker Compose services start after system boot

set -e

# Wait for Docker daemon to be ready
echo "Waiting for Docker daemon to start..."
while ! docker info > /dev/null 2>&1; do
    sleep 1
done
echo "Docker daemon is ready"

# Navigate to project directory
cd "/home/roboticslab/City College Dropbox/BO SHANG/NYCDOT_classification_project/nyc-traffic-monitor"

# Stop any existing containers
echo "Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Pull latest changes (optional)
# git pull origin main 2>/dev/null || true

# Build and start services
echo "Starting Docker Compose services..."
docker-compose up -d --build

# Show status
echo "Services started. Checking status..."
docker-compose ps

echo "UMDL2 services are running!"
echo "Frontend: http://localhost:5173"
echo "Backend: http://localhost:8001"