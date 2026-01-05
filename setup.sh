#!/bin/bash
# Setup script for VPN Telegram Bot

set -e

echo "🔧 VPN Telegram Bot Setup Script"
echo "=================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root or with sudo${NC}"
    exit 1
fi

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. Install Xray-core
print_info "Step 1: Installing Xray-core..."
if ! command -v xray &> /dev/null; then
    print_warning "Xray not found, installing..."
    bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install

    if command -v xray &> /dev/null; then
        print_info "✓ Xray installed successfully"
        xray version
    else
        print_error "Failed to install Xray"
        exit 1
    fi
else
    print_info "✓ Xray already installed"
    xray version
fi

# 2. Setup Xray config directory
print_info "Step 2: Setting up Xray configuration directory..."
mkdir -p /usr/local/etc/xray
mkdir -p /etc/xray

# Copy config file if exists in project
if [ -f "xray_config.json" ]; then
    print_info "Copying Xray config from project..."
    cp xray_config.json /usr/local/etc/xray/config.json
    print_info "✓ Xray config copied to /usr/local/etc/xray/config.json"
elif [ -f "xray_config_example.json" ]; then
    print_info "Copying Xray example config..."
    cp xray_config_example.json /usr/local/etc/xray/config.json
    print_warning "⚠ Using example config - please edit /usr/local/etc/xray/config.json with your settings"
else
    print_error "No Xray config file found in project directory"
    exit 1
fi

# Set permissions
chmod 644 /usr/local/etc/xray/config.json
chown root:root /usr/local/etc/xray/config.json
print_info "✓ Permissions set for Xray config"

# 3. Validate Xray config
print_info "Step 3: Validating Xray configuration..."
xray -test -config /usr/local/etc/xray/config.json
if [ $? -eq 0 ]; then
    print_info "✓ Xray config is valid"
else
    print_error "Xray config validation failed"
    exit 1
fi

# 4. Start Xray service
print_info "Step 4: Starting Xray service..."
systemctl enable xray
systemctl start xray

# Check if Xray is running
sleep 2
if systemctl is-active --quiet xray; then
    print_info "✓ Xray service is running"
else
    print_error "Failed to start Xray service"
    systemctl status xray
    exit 1
fi

# 5. Setup Python virtual environment
print_info "Step 5: Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_info "✓ Virtual environment created"
fi

# Activate venv and install dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
print_info "✓ Python dependencies installed"

# 6. Create .env file if not exists
if [ ! -f ".env" ]; then
    print_info "Step 6: Creating .env file..."
    cat > .env << EOF
# Telegram Bot Configuration
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=123456789,987654321

# Server Configuration
SERVER_DOMAIN=yourdomain.com
SERVER_IP=127.0.0.1

# Xray Configuration
XRAY_CONFIG_PATH=/usr/local/etc/xray/config.json
XRAY_API_PORT=10085
EOF
    print_warning "⚠ .env file created - please edit with your settings"
else
    print_info "✓ .env file already exists"
fi

# 7. Initialize database
print_info "Step 7: Initializing database..."
python3 -c "from database import init_db; init_db()"
print_info "✓ Database initialized"

# 8. Setup systemd service for bot
print_info "Step 8: Setting up systemd service..."
CURRENT_USER=$(logname)
PROJECT_DIR=$(pwd)

cat > /etc/systemd/system/vpn-bot.service << EOF
[Unit]
Description=VPN Telegram Bot
After=network.target xray.service

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
print_info "✓ Systemd service created"

# 9. Final checks
print_info "Step 9: Running final checks..."

# Check API port
if netstat -tlnp 2>/dev/null | grep -q ":10085 "; then
    print_info "✓ Xray API is listening on port 10085"
else
    print_warning "⚠ Xray API not accessible on port 10085"
fi

# Test XrayManager initialization
python3 -c "
import os
os.environ['XRAY_CONFIG_PATH'] = '/usr/local/etc/xray/config.json'
from xray_manager import XrayManager
xray = XrayManager()
inbounds = xray.get_available_inbounds()
print(f'Available inbounds: {len(inbounds)}')
" 2>/dev/null && print_info "✓ XrayManager test passed" || print_error "✗ XrayManager test failed"

# Summary
echo ""
echo "==================================="
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your bot token and admin IDs"
echo "2. Edit /usr/local/etc/xray/config.json with your domain/certificates"
echo "3. Start the bot: sudo systemctl start vpn-bot"
echo "4. Check bot logs: sudo journalctl -u vpn-bot -f"
echo ""
echo "Useful commands:"
echo "  - Bot status:   sudo systemctl status vpn-bot"
echo "  - Xray status:  sudo systemctl status xray"
echo "  - View logs:    sudo journalctl -u vpn-bot -f"
echo "  - Restart bot:  sudo systemctl restart vpn-bot"
echo ""
