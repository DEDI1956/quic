#!/bin/bash

# Script instalasi VPN Bot untuk VPS
# Pastikan menjalankan sebagai root

set -e

echo "======================================"
echo "  VPN Telegram Bot Installer"
echo "======================================"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "Error: Script ini harus dijalankan sebagai root (gunakan sudo)" 
   exit 1
fi

# Update system
echo "📦 Updating system packages..."
apt update -y
apt upgrade -y

# Install dependencies
echo "📦 Installing dependencies..."
apt install -y python3 python3-pip python3-venv curl wget unzip nginx certbot python3-certbot-nginx

# Install Xray-core
echo "🚀 Installing Xray-core..."
bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install

# Create Xray config directory
mkdir -p /etc/xray
mkdir -p /usr/local/etc/xray

# Enable and start Xray
systemctl enable xray
systemctl start xray

# Setup bot directory
echo "📁 Setting up bot directory..."
BOT_DIR="/opt/vpn-bot"
mkdir -p $BOT_DIR
cd $BOT_DIR

# Copy files (assuming they're in current directory)
if [ -f "/root/vpn-bot/bot.py" ]; then
    cp -r /root/vpn-bot/* $BOT_DIR/
else
    echo "⚠️  Bot files not found in /root/vpn-bot/"
    echo "Please upload bot files to /root/vpn-bot/ first"
    exit 1
fi

# Create Python virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python requirements
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup environment file
echo "⚙️  Setting up configuration..."
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    read -p "Enter your Telegram Bot Token: " BOT_TOKEN
    read -p "Enter your Telegram User ID (Admin): " ADMIN_ID
    read -p "Enter your domain name: " DOMAIN
    read -p "Enter your server IP: " SERVER_IP
    
    cat > .env << EOF
BOT_TOKEN=$BOT_TOKEN
ADMIN_IDS=$ADMIN_ID
SERVER_DOMAIN=$DOMAIN
SERVER_IP=$SERVER_IP
DATABASE_URL=sqlite:///./vpn_bot.db
EOF
    
    # Update config.json
    cat > config.json << EOF
{
  "telegram": {
    "bot_token": "$BOT_TOKEN",
    "admin_ids": [$ADMIN_ID]
  },
  "xray": {
    "api_port": 10085,
    "config_path": "/usr/local/etc/xray/config.json"
  },
  "server": {
    "domain": "$DOMAIN",
    "ip": "$SERVER_IP"
  },
  "pricing": {
    "vmess_ws": 10000,
    "vmess_ws_tls": 12000,
    "vless_ws": 12000,
    "vless_ws_tls": 15000,
    "vless_tcp_tls": 18000,
    "trojan_ws": 15000,
    "trojan_ws_tls": 18000,
    "trojan_tcp_tls": 20000
  },
  "trial": {
    "enabled": true,
    "duration_hours": 1
  }
}
EOF
fi

# Generate SSL certificate
echo "🔐 Setting up SSL certificate..."
if [ ! -z "$DOMAIN" ]; then
    echo "Generating SSL certificate for $DOMAIN..."
    certbot certonly --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN || true
    
    # Copy certificates for Xray
    if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
        cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /etc/xray/cert.crt
        cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /etc/xray/cert.key
    else
        # Generate self-signed certificate
        echo "Generating self-signed certificate..."
        openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 \
            -subj "/CN=$DOMAIN" \
            -keyout /etc/xray/cert.key \
            -out /etc/xray/cert.crt
    fi
fi

# Create systemd service for bot
echo "🤖 Creating systemd service..."
cat > /etc/systemd/system/vpn-bot.service << EOF
[Unit]
Description=VPN Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$BOT_DIR
Environment="PATH=$BOT_DIR/venv/bin"
ExecStart=$BOT_DIR/venv/bin/python3 $BOT_DIR/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Initialize database
echo "💾 Initializing database..."
python3 << EOF
from database import init_db
init_db()
print("Database initialized successfully!")
EOF

# Configure firewall
echo "🔥 Configuring firewall..."
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8080/tcp
ufw allow 8443/tcp
ufw allow 445/tcp
ufw allow 8081/tcp
ufw allow 22/tcp
ufw --force enable

# Enable and start bot service
echo "🚀 Starting bot service..."
systemctl daemon-reload
systemctl enable vpn-bot
systemctl start vpn-bot

# Restart Xray
systemctl restart xray

echo ""
echo "======================================"
echo "  ✅ Installation Complete!"
echo "======================================"
echo ""
echo "📊 Service Status:"
systemctl status vpn-bot --no-pager || true
echo ""
echo "🔧 Useful Commands:"
echo "  • Check bot status: systemctl status vpn-bot"
echo "  • View bot logs: journalctl -u vpn-bot -f"
echo "  • Restart bot: systemctl restart vpn-bot"
echo "  • Check Xray status: systemctl status xray"
echo "  • View Xray logs: journalctl -u xray -f"
echo ""
echo "📝 Configuration files:"
echo "  • Bot directory: $BOT_DIR"
echo "  • Environment: $BOT_DIR/.env"
echo "  • Config: $BOT_DIR/config.json"
echo "  • Xray config: /usr/local/etc/xray/config.json"
echo ""
echo "🎉 Your bot is now running!"
echo "Open Telegram and start chatting with your bot!"
echo ""
