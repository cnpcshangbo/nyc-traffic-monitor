#!/bin/bash
# Setup passwordless sudo for roboticslab user (for Claude Code automation)

echo "🔐 Setting up passwordless sudo for roboticslab user..."
echo "This will allow Claude Code to run system administration commands automatically."
echo ""

# Create sudoers configuration for roboticslab user
SUDOERS_FILE="/etc/sudoers.d/roboticslab-nopasswd"

# Check if configuration already exists
if [ -f "$SUDOERS_FILE" ]; then
    echo "⚠️  Passwordless sudo configuration already exists:"
    sudo cat "$SUDOERS_FILE"
    echo ""
    read -p "Replace existing configuration? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

echo "Creating sudoers configuration..."
echo "# Allow roboticslab user to run sudo commands without password" | sudo tee "$SUDOERS_FILE" > /dev/null
echo "# This enables Claude Code to perform system administration tasks" | sudo tee -a "$SUDOERS_FILE" > /dev/null
echo "roboticslab ALL=(ALL) NOPASSWD: ALL" | sudo tee -a "$SUDOERS_FILE" > /dev/null

# Set correct permissions
sudo chmod 440 "$SUDOERS_FILE"

# Verify configuration
echo ""
echo "✅ Configuration created:"
sudo cat "$SUDOERS_FILE"

echo ""
echo "🧪 Testing passwordless sudo..."
if sudo -n whoami > /dev/null 2>&1; then
    echo "✅ Passwordless sudo is working!"
    echo "   User: $(sudo -n whoami)"
else
    echo "❌ Passwordless sudo test failed. You may need to:"
    echo "   1. Restart your terminal session"
    echo "   2. Log out and log back in"
    echo "   3. Check the sudoers file syntax with: sudo visudo -c"
fi

echo ""
echo "🚨 SECURITY NOTE:"
echo "   This configuration allows the 'roboticslab' user to run ANY command"
echo "   with sudo without a password. This is convenient for automation but"
echo "   reduces security. Use with caution on production systems."
echo ""
echo "   To remove this configuration later:"
echo "   sudo rm '$SUDOERS_FILE'"