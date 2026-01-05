#!/bin/bash

# Real-time Monitoring Script
# Monitor bot and Xray in real-time

echo "======================================"
echo "  VPN Bot Real-time Monitor"
echo "======================================"
echo "Press Ctrl+C to exit"
echo ""

while true; do
    clear
    echo "======================================"
    echo "  VPN Bot Monitor - $(date '+%Y-%m-%d %H:%M:%S')"
    echo "======================================"
    echo ""
    
    # Bot Status
    if systemctl is-active --quiet vpn-bot; then
        echo "🤖 Bot: ✅ RUNNING"
    else
        echo "🤖 Bot: ❌ STOPPED"
    fi
    
    # Xray Status
    if systemctl is-active --quiet xray; then
        echo "🚀 Xray: ✅ RUNNING"
    else
        echo "🚀 Xray: ❌ STOPPED"
    fi
    
    echo ""
    
    # Resource Usage
    echo "📊 RESOURCE USAGE"
    echo "------------------------------------"
    
    # CPU
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    echo "⚡ CPU: ${CPU_USAGE}%"
    
    # Memory
    MEM_INFO=$(free -m | awk 'NR==2{printf "🧠 Memory: %s/%s MB (%.0f%%)", $3, $2, $3*100/$2}')
    echo "$MEM_INFO"
    
    # Disk
    DISK_INFO=$(df -h / | awk 'NR==2{printf "💾 Disk: %s/%s (%s)", $3, $2, $5}')
    echo "$DISK_INFO"
    
    # Load Average
    LOAD=$(uptime | awk -F'load average:' '{print $2}')
    echo "📈 Load:$LOAD"
    
    echo ""
    
    # Network
    echo "🌐 NETWORK"
    echo "------------------------------------"
    
    # Active Connections
    CONNECTIONS=$(netstat -an | grep ESTABLISHED | wc -l)
    echo "🔗 Active Connections: $CONNECTIONS"
    
    # Xray Ports
    echo "🔌 Xray Ports:"
    netstat -tulpn | grep xray | awk '{print "   Port", $4}' | sed 's/.*://' | sort -u
    
    echo ""
    
    # Recent Activity
    echo "📋 RECENT ACTIVITY (Last 3 logs)"
    echo "------------------------------------"
    journalctl -u vpn-bot -n 3 --no-pager --output=short-precise | tail -3
    
    echo ""
    echo "======================================"
    
    # Wait 5 seconds before refresh
    sleep 5
done
