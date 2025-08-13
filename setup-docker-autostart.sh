#!/bin/bash

# Setup script for Docker Compose auto-start on system boot

set -e

echo "========================================="
echo "UMDL2 Docker Auto-Start Setup"
echo "========================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "Please run this script as a regular user with sudo privileges"
   exit 1
fi

# Install Docker and Docker Compose if not already installed
echo "[1/5] Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "Docker installed successfully"
else
    echo "✓ Docker is already installed"
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    sudo apt-get update
    sudo apt-get install -y docker-compose
    echo "Docker Compose installed successfully"
else
    echo "✓ Docker Compose is already installed"
fi

# Copy systemd service file
echo "[2/5] Installing systemd service..."
sudo cp umdl2.service /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/umdl2.service
echo "✓ Service file installed"

# Reload systemd daemon
echo "[3/5] Reloading systemd daemon..."
sudo systemctl daemon-reload
echo "✓ Systemd daemon reloaded"

# Enable service to start on boot
echo "[4/5] Enabling auto-start on boot..."
sudo systemctl enable umdl2.service
echo "✓ Auto-start enabled"

# Build Docker images
echo "[5/5] Building Docker images..."
docker-compose build
echo "✓ Docker images built"

echo ""
echo "========================================="
echo "✅ Setup Complete!"
echo "========================================="
echo ""
echo "Service Management Commands:"
echo "  Start services:   sudo systemctl start umdl2"
echo "  Stop services:    sudo systemctl stop umdl2"
echo "  Check status:     sudo systemctl status umdl2"
echo "  View logs:        docker-compose logs -f"
echo ""
echo "Docker Compose Commands:"
echo "  Start manually:   docker-compose up -d"
echo "  Stop manually:    docker-compose down"
echo "  Rebuild:          docker-compose up -d --build"
echo ""
echo "The services will automatically start on system boot."
echo ""
echo "Would you like to start the services now? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo "Starting services..."
    sudo systemctl start umdl2
    sleep 5
    sudo systemctl status umdl2 --no-pager
    echo ""
    echo "Services are running!"
    echo "Frontend: http://localhost:5173"
    echo "Backend:  http://localhost:8001"
fi