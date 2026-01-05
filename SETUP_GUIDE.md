# Setup Guide - VPN Telegram Bot

## Prerequisites

### System Requirements
- Ubuntu 20.04/22.04 or Debian 10/11
- Minimum 1GB RAM, 1 Core CPU
- Python 3.10+
- Xray-core installed

## Installation

### 1. Install Xray-core

```bash
# Install Xray-core
bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install

# Verify installation
xray version
```

### 2. Setup Configuration Files

The bot requires a properly configured Xray config file with all necessary inbounds.

**Copy the example config:**
```bash
sudo mkdir -p /usr/local/etc/xray
sudo cp xray_config.json /usr/local/etc/xray/config.json
```

**Or use the project config (for testing):**
```bash
# Update config.json to point to the correct location
```

### 3. Configure the Bot

Edit `config.json`:

```json
{
  "telegram": {
    "bot_token": "YOUR_BOT_TOKEN_FROM_BOTFATHER",
    "admin_ids": [123456789, 987654321]
  },
  "xray": {
    "api_port": 10085,
    "config_path": "/usr/local/etc/xray/config.json"
  },
  "server": {
    "domain": "yourdomain.com",
    "ip": "your.server.ip"
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
```

### 4. Install Python Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Setup Environment Variables (Optional)

Create `.env` file:
```bash
BOT_TOKEN=your_bot_token
ADMIN_IDS=123456789,987654321
SERVER_DOMAIN=yourdomain.com
SERVER_IP=1.2.3.4
XRAY_CONFIG_PATH=/usr/local/etc/xray/config.json
XRAY_API_PORT=10085
```

### 6. Initialize Database

```bash
python3 -c "from database import init_db; init_db()"
```

### 7. Setup Systemd Service

Create `/etc/systemd/system/vpn-bot.service`:

```ini
[Unit]
Description=VPN Telegram Bot
After=network.target xray.service

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/vpn-bot
Environment="PATH=/home/your_username/vpn-bot/venv/bin"
ExecStart=/home/your_username/vpn-bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable vpn-bot
sudo systemctl start vpn-bot
sudo systemctl status vpn-bot
```

## Troubleshooting

### Error: "CRITICAL: Xray config missing 'inbounds' array"

**Cause:** The Xray config file doesn't exist or has invalid JSON.

**Solution:**
```bash
# Check if config exists
ls -la /usr/local/etc/xray/config.json

# If missing, copy from example
sudo cp xray_config_example.json /usr/local/etc/xray/config.json

# Verify JSON is valid
python3 -c "import json; json.load(open('/usr/local/etc/xray/config.json'))"
```

### Error: "Xray unhealthy" / "Xray service not running"

**Cause:** Xray service is not installed or not running.

**Solution:**
```bash
# Check Xray service status
sudo systemctl status xray

# If not installed:
bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install

# Start Xray
sudo systemctl start xray
sudo systemctl enable xray
```

### Error: "Xray API not reachable on 127.0.0.1:10085"

**Cause:** Xray API inbound is not configured or blocked.

**Solution:**
```bash
# Check if API port is listening
sudo netstat -tlnp | grep 10085

# If not listening, ensure config has API inbound:
# {
#   "port": 10085,
#   "protocol": "dokodemo-door",
#   "tag": "api",
#   "settings": {"address": "127.0.0.1"}
# }

# Reload Xray config
sudo systemctl reload xray
```

### Error: Permission denied writing to Xray config

**Cause:** Bot doesn't have write permission to Xray config.

**Solution:**
```bash
# Set proper permissions
sudo chmod 644 /usr/local/etc/xray/config.json
sudo chown root:root /usr/local/etc/xray/config.json

# If running bot as non-root, add to xray group (create if needed)
sudo groupadd xray
sudo usermod -aG xray your_username

# Update group permissions
sudo chown :xray /usr/local/etc/xray/config.json
sudo chmod 664 /usr/local/etc/xray/config.json
```

## Testing

### Test Xray Configuration

```bash
# Test XrayManager initialization
python3 -c "
import os
os.environ['XRAY_CONFIG_PATH'] = '/usr/local/etc/xray/config.json'
from xray_manager import XrayManager
xray = XrayManager()
print('Config loaded:', xray.config_path)
print('Inbounds:', xray.get_available_inbounds())
"
```

### Test Bot Initialization

```bash
python3 test_bot_init.py
```

### Test Trial Creation

1. Start the bot: `python3 bot.py`
2. In Telegram, send `/start`
3. Click "🎁 Trial Gratis"
4. Select a protocol
5. You should receive a VPN link (or error if Xray not running)

## Production Checklist

- [ ] Xray-core installed and running
- [ ] Xray config properly configured with all inbounds
- [ ] Bot token from @BotFather
- [ ] Admin IDs configured
- [ ] Domain configured (if using TLS)
- [ ] SSL/TLS certificates installed (if using TLS)
- [ ] Firewall ports open: 80, 443, 8080, 8443, 445, 8081, 10085
- [ ] Database initialized
- [ ] Bot service running with systemd
- [ ] Xray service running with systemd
- [ ] Logs monitoring setup: `journalctl -u vpn-bot -f`

## Available Inbounds

The bot supports the following inbound configurations (must exist in Xray config):

| Tag | Protocol | Port | Network | Security |
|-----|----------|------|---------|----------|
| vmess-ws | VMess | 8080 | WebSocket | None |
| vmess-ws-tls | VMess | 8443 | WebSocket | TLS |
| vless-ws | VLess | 80 | WebSocket | None |
| vless-ws-tls | VLess | 443 | WebSocket | TLS |
| vless-tcp | VLess | 8082 | TCP | None |
| vless-tcp-tls | VLess | 8444 | TCP | TLS |
| trojan-ws-tls | Trojan | 445 | WebSocket | TLS |
| trojan-tcp-tls | Trojan | 8081 | TCP | TLS |

**Note:** For non-TLS inbounds, you can use IP address instead of domain. For TLS inbounds, you need a valid domain and SSL certificates.
