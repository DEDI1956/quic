#!/bin/bash

# System Check Script
# Memeriksa status semua komponen bot VPN

echo "======================================"
echo "  VPN Bot System Check"
echo "======================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}❌ Please run as root (use sudo)${NC}"
   exit 1
fi

# Check Bot Service
echo "🤖 Checking VPN Bot Service..."
if systemctl is-active --quiet vpn-bot; then
    echo -e "${GREEN}✅ Bot is running${NC}"
else
    echo -e "${RED}❌ Bot is not running${NC}"
    echo "   Run: systemctl start vpn-bot"
fi
echo ""

# Check Xray Service
echo "🚀 Checking Xray Service..."
if systemctl is-active --quiet xray; then
    echo -e "${GREEN}✅ Xray is running${NC}"
else
    echo -e "${RED}❌ Xray is not running${NC}"
    echo "   Run: systemctl start xray"
fi
echo ""

# Check Ports
echo "🔌 Checking Ports..."
PORTS=(80 443 8080 8443 445 8081)
for port in "${PORTS[@]}"; do
    if netstat -tuln | grep -q ":$port "; then
        echo -e "${GREEN}✅ Port $port is open${NC}"
    else
        echo -e "${YELLOW}⚠️  Port $port is not listening${NC}"
    fi
done
echo ""

# Check Disk Space
echo "💾 Checking Disk Space..."
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -lt 80 ]; then
    echo -e "${GREEN}✅ Disk usage: ${DISK_USAGE}%${NC}"
else
    echo -e "${YELLOW}⚠️  Disk usage: ${DISK_USAGE}% (High)${NC}"
fi
echo ""

# Check Memory
echo "🧠 Checking Memory..."
MEM_USAGE=$(free | awk '/Mem:/ {printf("%.0f", $3/$2 * 100)}')
if [ $MEM_USAGE -lt 80 ]; then
    echo -e "${GREEN}✅ Memory usage: ${MEM_USAGE}%${NC}"
else
    echo -e "${YELLOW}⚠️  Memory usage: ${MEM_USAGE}% (High)${NC}"
fi
echo ""

# Check CPU Load
echo "⚡ Checking CPU Load..."
CPU_LOAD=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
echo -e "${GREEN}📊 Load average: ${CPU_LOAD}${NC}"
echo ""

# Check Database
echo "🗄️  Checking Database..."
if [ -f "/opt/vpn-bot/vpn_bot.db" ]; then
    DB_SIZE=$(du -h /opt/vpn-bot/vpn_bot.db | awk '{print $1}')
    echo -e "${GREEN}✅ Database exists (${DB_SIZE})${NC}"
else
    echo -e "${RED}❌ Database not found${NC}"
fi
echo ""

# Check SSL Certificate
echo "🔐 Checking SSL Certificate..."
if [ -f "/etc/xray/cert.crt" ]; then
    CERT_EXPIRY=$(openssl x509 -enddate -noout -in /etc/xray/cert.crt | cut -d= -f2)
    echo -e "${GREEN}✅ Certificate expires: ${CERT_EXPIRY}${NC}"
else
    echo -e "${YELLOW}⚠️  Certificate not found${NC}"
fi
echo ""

# Check Firewall
echo "🔥 Checking Firewall..."
if command -v ufw &> /dev/null; then
    if ufw status | grep -q "Status: active"; then
        echo -e "${GREEN}✅ Firewall is active${NC}"
    else
        echo -e "${YELLOW}⚠️  Firewall is inactive${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  UFW not installed${NC}"
fi
echo ""

# Recent Logs
echo "📋 Recent Bot Logs (last 5 lines)..."
journalctl -u vpn-bot -n 5 --no-pager
echo ""

# Statistics
echo "📊 Bot Statistics..."
cd /opt/vpn-bot
source venv/bin/activate
python3 manage.py stats 2>/dev/null || echo "Unable to get statistics"
echo ""

echo "======================================"
echo "  System Check Complete"
echo "======================================"
echo ""
echo "💡 Tips:"
echo "  • View full logs: journalctl -u vpn-bot -f"
echo "  • Restart bot: systemctl restart vpn-bot"
echo "  • Check Xray: systemctl status xray"
echo ""
