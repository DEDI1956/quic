#!/bin/bash

# Setup cron jobs for VPN Bot maintenance

BOT_DIR="/opt/vpn-bot"
PYTHON="$BOT_DIR/venv/bin/python3"

# Create directories
mkdir -p $BOT_DIR/backups
mkdir -p $BOT_DIR/reports
mkdir -p $BOT_DIR/logs

# Create cron jobs
echo "Setting up cron jobs..."

# Add to crontab
(crontab -l 2>/dev/null; echo "# VPN Bot Maintenance Tasks") | crontab -

# Cleanup expired accounts every hour
(crontab -l 2>/dev/null; echo "0 * * * * $PYTHON $BOT_DIR/cron_tasks.py cleanup >> $BOT_DIR/logs/cron.log 2>&1") | crontab -

# Send expiry reminders every 6 hours
(crontab -l 2>/dev/null; echo "0 */6 * * * $PYTHON $BOT_DIR/cron_tasks.py reminders >> $BOT_DIR/logs/cron.log 2>&1") | crontab -

# Generate daily report at 23:00
(crontab -l 2>/dev/null; echo "0 23 * * * $PYTHON $BOT_DIR/cron_tasks.py report >> $BOT_DIR/logs/cron.log 2>&1") | crontab -

# Backup database daily at 02:00
(crontab -l 2>/dev/null; echo "0 2 * * * $PYTHON $BOT_DIR/cron_tasks.py backup >> $BOT_DIR/logs/cron.log 2>&1") | crontab -

# Restart bot daily at 04:00 (maintenance)
(crontab -l 2>/dev/null; echo "0 4 * * * systemctl restart vpn-bot >> $BOT_DIR/logs/cron.log 2>&1") | crontab -

# Restart Xray weekly on Sunday at 03:00
(crontab -l 2>/dev/null; echo "0 3 * * 0 systemctl restart xray >> $BOT_DIR/logs/cron.log 2>&1") | crontab -

# Clean old logs (keep last 30 days)
(crontab -l 2>/dev/null; echo "0 5 * * * find $BOT_DIR/logs -name '*.log' -mtime +30 -delete") | crontab -

echo "✅ Cron jobs setup completed!"
echo ""
echo "Configured tasks:"
echo "• Hourly: Cleanup expired accounts"
echo "• Every 6h: Send expiry reminders"
echo "• Daily 23:00: Generate report"
echo "• Daily 02:00: Backup database"
echo "• Daily 04:00: Restart bot"
echo "• Weekly Sunday 03:00: Restart Xray"
echo "• Daily 05:00: Clean old logs"
echo ""
echo "View cron jobs: crontab -l"
echo "View cron logs: tail -f $BOT_DIR/logs/cron.log"
