#!/bin/bash
# Fix UMDL2 service configuration script

echo "🔧 Fixing UMDL2 service configuration..."

# Stop the failing service
echo "Stopping UMDL2 service..."
sudo systemctl stop umdl2.service

# Copy the corrected service file
echo "Installing corrected service file..."
sudo cp "/home/roboticslab/City College Dropbox/BO SHANG/NYCDOT_classification_project/nyc-traffic-monitor/umdl2.service" /etc/systemd/system/

# Reload systemd daemon
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable and start the service
echo "Enabling and starting UMDL2 service..."
sudo systemctl enable umdl2.service
sudo systemctl start umdl2.service

# Check status
echo "Checking service status..."
sudo systemctl status umdl2.service

echo "✅ Service configuration fixed!"
echo ""
echo "📋 Service Summary:"
echo "  - Docker service: $(systemctl is-enabled docker.service) ($(systemctl is-active docker.service))"
echo "  - UMDL2 service: $(systemctl is-enabled umdl2.service) ($(systemctl is-active umdl2.service))"
echo ""
echo "🚀 The service will now auto-start on Ubuntu reboots!"