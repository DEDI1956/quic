# Quick Reference - VPN Telegram Bot

Referensi cepat untuk command dan operasi umum.

## 🚀 Quick Start

### Instalasi Baru
```bash
chmod +x install.sh
./install.sh
```

### Development/Testing
```bash
chmod +x quick_start.sh
./quick_start.sh
python3 bot.py
```

## 🔧 Management Commands

### User Management
```bash
# Add admin
python3 manage.py add-admin 123456789

# Add balance
python3 manage.py add-balance 123456789 50000

# List all users
python3 manage.py list-users

# Show statistics
python3 manage.py stats
```

### Account Management
```bash
# List active accounts
python3 manage.py list-accounts

# Delete account
python3 manage.py delete-account 123

# Cleanup expired accounts
python3 manage.py cleanup
```

### Database
```bash
# Initialize database
python3 manage.py init

# Backup database
./backup.sh

# Restore from backup
./restore.sh /path/to/backup.tar.gz
```

## 🤖 Service Management

### Bot Service
```bash
# Start bot
systemctl start vpn-bot

# Stop bot
systemctl stop vpn-bot

# Restart bot
systemctl restart vpn-bot

# Check status
systemctl status vpn-bot

# View logs
journalctl -u vpn-bot -f

# View last 50 logs
journalctl -u vpn-bot -n 50
```

### Xray Service
```bash
# Start Xray
systemctl start xray

# Stop Xray
systemctl stop xray

# Restart Xray
systemctl restart xray

# Check status
systemctl status xray

# Test config
xray -test -config /usr/local/etc/xray/config.json

# View logs
journalctl -u xray -f
```

## 📊 Monitoring

### System Check
```bash
# Full system check
./check_system.sh

# Real-time monitoring
./monitor.sh

# Resource usage
htop

# Disk space
df -h

# Network connections
netstat -tulpn | grep xray
```

### View Logs
```bash
# Bot logs
tail -f /var/log/syslog | grep vpn-bot

# Xray logs
journalctl -u xray -f

# Cron logs
tail -f /opt/vpn-bot/logs/cron.log

# All system logs
journalctl -f
```

## 🔐 Security

### Firewall
```bash
# Check firewall status
ufw status

# Enable firewall
ufw enable

# Allow port
ufw allow 8080/tcp

# Delete rule
ufw delete allow 8080/tcp

# Reset firewall
ufw reset
```

### SSL Certificate
```bash
# Renew certificate
certbot renew

# Force renew
certbot renew --force-renewal

# Copy to Xray
cp /etc/letsencrypt/live/DOMAIN/fullchain.pem /etc/xray/cert.crt
cp /etc/letsencrypt/live/DOMAIN/privkey.pem /etc/xray/cert.key

# Restart Xray
systemctl restart xray
```

## 📝 Configuration Files

### Bot Config
```bash
# Edit bot config
nano /opt/vpn-bot/config.json

# Edit environment
nano /opt/vpn-bot/.env

# Restart after changes
systemctl restart vpn-bot
```

### Xray Config
```bash
# Edit Xray config
nano /usr/local/etc/xray/config.json

# Test config
xray -test -config /usr/local/etc/xray/config.json

# Restart after changes
systemctl restart xray
```

## 🔄 Maintenance Tasks

### Daily
```bash
# Check system
./check_system.sh

# View statistics
python3 manage.py stats

# Cleanup expired
python3 manage.py cleanup
```

### Weekly
```bash
# Backup database
./backup.sh

# Update system
apt update && apt upgrade -y

# Restart services
systemctl restart vpn-bot
systemctl restart xray
```

### Monthly
```bash
# Check disk space
df -h

# Clean old logs
find /var/log -name "*.log" -mtime +30 -delete

# Review user accounts
python3 manage.py list-users

# Check SSL expiry
openssl x509 -enddate -noout -in /etc/xray/cert.crt
```

## 🐛 Troubleshooting

### Bot Not Starting
```bash
# Check status
systemctl status vpn-bot

# View errors
journalctl -u vpn-bot -n 50

# Test manually
cd /opt/vpn-bot
source venv/bin/activate
python3 bot.py

# Check environment
cat .env

# Reinstall dependencies
pip install -r requirements.txt
```

### Xray Not Working
```bash
# Check status
systemctl status xray

# Test config
xray -test -config /usr/local/etc/xray/config.json

# Check ports
netstat -tulpn | grep xray

# Restart
systemctl restart xray
```

### Connection Issues
```bash
# Check firewall
ufw status

# Check ports
netstat -tulpn | grep -E '(80|443|8080|8443|445|8081)'

# Test domain resolution
nslookup yourdomain.com

# Check SSL
openssl s_client -connect yourdomain.com:443
```

### Database Issues
```bash
# Check database file
ls -lh /opt/vpn-bot/vpn_bot.db

# Backup current
cp /opt/vpn-bot/vpn_bot.db /tmp/backup.db

# Reinitialize (WARNING: deletes data)
rm /opt/vpn-bot/vpn_bot.db
python3 manage.py init

# Restore from backup
cp /tmp/backup.db /opt/vpn-bot/vpn_bot.db
```

## 📞 Common Issues & Solutions

### Issue: Bot tidak merespons
```bash
systemctl restart vpn-bot
journalctl -u vpn-bot -n 50
```

### Issue: Akun tidak bisa connect
```bash
systemctl restart xray
xray -test -config /usr/local/etc/xray/config.json
```

### Issue: Port sudah digunakan
```bash
netstat -tulpn | grep :PORT
kill PID
systemctl restart xray
```

### Issue: SSL Error
```bash
certbot renew
cp /etc/letsencrypt/live/*/fullchain.pem /etc/xray/cert.crt
cp /etc/letsencrypt/live/*/privkey.pem /etc/xray/cert.key
systemctl restart xray
```

### Issue: Disk penuh
```bash
df -h
du -sh /var/log/*
journalctl --vacuum-time=7d
apt clean
```

## 💡 Pro Tips

### Performance
```bash
# Enable BBR (better congestion control)
echo "net.core.default_qdisc=fq" >> /etc/sysctl.conf
echo "net.ipv4.tcp_congestion_control=bbr" >> /etc/sysctl.conf
sysctl -p

# Increase file descriptors
echo "* soft nofile 51200" >> /etc/security/limits.conf
echo "* hard nofile 51200" >> /etc/security/limits.conf
```

### Automation
```bash
# Setup cron jobs
./setup_cron.sh

# View cron jobs
crontab -l

# Edit cron jobs
crontab -e
```

### Backup
```bash
# Auto backup script in cron
echo "0 2 * * * /opt/vpn-bot/backup.sh" | crontab -

# Backup to external storage
scp /opt/vpn-bot/backups/*.tar.gz user@backup-server:/backups/
```

## 🎯 Quick Fixes

```bash
# Restart everything
systemctl restart vpn-bot xray nginx

# Kill all connections
pkill -9 xray
systemctl start xray

# Reset firewall
ufw disable
ufw --force reset
ufw allow 22,80,443,8080,8443,445,8081/tcp
ufw enable

# Clean everything
systemctl stop vpn-bot xray
rm -rf /opt/vpn-bot/venv
cd /opt/vpn-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
systemctl start vpn-bot xray
```

## 📱 Test Connection

```bash
# Test bot
curl https://api.telegram.org/botTOKEN/getMe

# Test Xray port
nc -zv localhost 8080

# Test from outside
curl -I http://YOUR_IP:8080

# Test HTTPS
curl -I https://YOUR_DOMAIN:443
```

## 🔗 Important Paths

```
/opt/vpn-bot/                 # Bot directory
/opt/vpn-bot/bot.py          # Main bot file
/opt/vpn-bot/.env            # Environment config
/opt/vpn-bot/config.json     # Bot config
/opt/vpn-bot/vpn_bot.db      # Database
/opt/vpn-bot/backups/        # Backups
/opt/vpn-bot/logs/           # Logs

/usr/local/etc/xray/         # Xray config directory
/etc/xray/                   # Xray certificates
/etc/systemd/system/vpn-bot.service  # Bot service
```

## 📚 More Help

- Full documentation: `README.md`
- Indonesian guide: `INSTALLATION_ID.md`
- FAQ: `FAQ.md`
- Apps guide: `APPS_GUIDE.md`
- Changelog: `CHANGELOG.md`

---

**Keep this file handy for quick reference!** 📌
