#!/bin/bash

# Backup Script for VPN Bot
# Creates backup of database and configurations

BACKUP_DIR="/opt/vpn-bot/backups"
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_NAME="vpn-bot-backup-${DATE}"

echo "======================================"
echo "  VPN Bot Backup"
echo "======================================"
echo ""

# Create backup directory
mkdir -p $BACKUP_DIR/$BACKUP_NAME

echo "📦 Creating backup: $BACKUP_NAME"
echo ""

# Backup Database
if [ -f "/opt/vpn-bot/vpn_bot.db" ]; then
    echo "💾 Backing up database..."
    cp /opt/vpn-bot/vpn_bot.db $BACKUP_DIR/$BACKUP_NAME/
    echo "   ✅ Database backed up"
else
    echo "   ⚠️  Database not found"
fi

# Backup Configurations
echo "⚙️  Backing up configurations..."
cp /opt/vpn-bot/.env $BACKUP_DIR/$BACKUP_NAME/ 2>/dev/null || echo "   ⚠️  .env not found"
cp /opt/vpn-bot/config.json $BACKUP_DIR/$BACKUP_NAME/ 2>/dev/null || echo "   ⚠️  config.json not found"
echo "   ✅ Configurations backed up"

# Backup Xray Config
echo "🚀 Backing up Xray config..."
mkdir -p $BACKUP_DIR/$BACKUP_NAME/xray
cp /usr/local/etc/xray/config.json $BACKUP_DIR/$BACKUP_NAME/xray/ 2>/dev/null || echo "   ⚠️  Xray config not found"
cp /etc/xray/cert.crt $BACKUP_DIR/$BACKUP_NAME/xray/ 2>/dev/null
cp /etc/xray/cert.key $BACKUP_DIR/$BACKUP_NAME/xray/ 2>/dev/null
echo "   ✅ Xray config backed up"

# Create archive
echo "📦 Creating archive..."
cd $BACKUP_DIR
tar -czf ${BACKUP_NAME}.tar.gz $BACKUP_NAME
rm -rf $BACKUP_NAME

BACKUP_SIZE=$(du -h ${BACKUP_NAME}.tar.gz | awk '{print $1}')

echo ""
echo "======================================"
echo "  ✅ Backup Complete!"
echo "======================================"
echo ""
echo "📁 Backup file: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"
echo "📊 Size: $BACKUP_SIZE"
echo ""

# Clean old backups (keep last 7 days)
echo "🧹 Cleaning old backups..."
find $BACKUP_DIR -name "vpn-bot-backup-*.tar.gz" -mtime +7 -delete
REMAINING=$(ls -1 $BACKUP_DIR/vpn-bot-backup-*.tar.gz 2>/dev/null | wc -l)
echo "   📂 Total backups: $REMAINING"
echo ""

echo "💡 To restore backup:"
echo "   tar -xzf $BACKUP_DIR/${BACKUP_NAME}.tar.gz -C /tmp/"
echo "   cp /tmp/${BACKUP_NAME}/* /opt/vpn-bot/"
echo ""
