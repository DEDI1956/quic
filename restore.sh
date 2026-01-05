#!/bin/bash

# Restore Script for VPN Bot
# Restores backup of database and configurations

if [ -z "$1" ]; then
    echo "Usage: ./restore.sh <backup-file.tar.gz>"
    echo ""
    echo "Available backups:"
    ls -lh /opt/vpn-bot/backups/*.tar.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE=$1
TEMP_DIR="/tmp/vpn-bot-restore-$$"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "======================================"
echo "  VPN Bot Restore"
echo "======================================"
echo ""
echo "⚠️  WARNING: This will overwrite current data!"
read -p "Continue? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Restore cancelled."
    exit 1
fi

echo ""
echo "📦 Extracting backup..."
mkdir -p $TEMP_DIR
tar -xzf $BACKUP_FILE -C $TEMP_DIR

BACKUP_NAME=$(ls $TEMP_DIR)

if [ -z "$BACKUP_NAME" ]; then
    echo "❌ Invalid backup file"
    rm -rf $TEMP_DIR
    exit 1
fi

echo "   ✅ Backup extracted"
echo ""

# Stop services
echo "🛑 Stopping services..."
systemctl stop vpn-bot
systemctl stop xray
echo "   ✅ Services stopped"
echo ""

# Restore Database
if [ -f "$TEMP_DIR/$BACKUP_NAME/vpn_bot.db" ]; then
    echo "💾 Restoring database..."
    cp $TEMP_DIR/$BACKUP_NAME/vpn_bot.db /opt/vpn-bot/
    echo "   ✅ Database restored"
else
    echo "   ⚠️  Database not found in backup"
fi

# Restore Configurations
echo "⚙️  Restoring configurations..."
if [ -f "$TEMP_DIR/$BACKUP_NAME/.env" ]; then
    cp $TEMP_DIR/$BACKUP_NAME/.env /opt/vpn-bot/
    echo "   ✅ .env restored"
fi

if [ -f "$TEMP_DIR/$BACKUP_NAME/config.json" ]; then
    cp $TEMP_DIR/$BACKUP_NAME/config.json /opt/vpn-bot/
    echo "   ✅ config.json restored"
fi

# Restore Xray Config
if [ -d "$TEMP_DIR/$BACKUP_NAME/xray" ]; then
    echo "🚀 Restoring Xray config..."
    cp $TEMP_DIR/$BACKUP_NAME/xray/config.json /usr/local/etc/xray/ 2>/dev/null
    cp $TEMP_DIR/$BACKUP_NAME/xray/cert.crt /etc/xray/ 2>/dev/null
    cp $TEMP_DIR/$BACKUP_NAME/xray/cert.key /etc/xray/ 2>/dev/null
    echo "   ✅ Xray config restored"
fi

# Cleanup
rm -rf $TEMP_DIR

# Start services
echo ""
echo "🚀 Starting services..."
systemctl start xray
systemctl start vpn-bot
echo "   ✅ Services started"

echo ""
echo "======================================"
echo "  ✅ Restore Complete!"
echo "======================================"
echo ""
echo "🔍 Verify services:"
echo "   systemctl status vpn-bot"
echo "   systemctl status xray"
echo ""
