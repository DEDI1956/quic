# VPN Telegram Bot - Bot Jualan Akun VPN

Bot Telegram lengkap untuk menjual akun VPN dengan berbagai protokol (VMess, VLess, Trojan) dan koneksi (WebSocket, TCP, SSL/TLS, UDP).

## ✨ Fitur Utama

### 🎯 Fitur User
- **Beli Akun VPN** - Berbagai pilihan protokol dan durasi
- **Trial Gratis** - Trial 1 jam untuk testing
- **Manajemen Akun** - Lihat, kelola, dan renew akun
- **Top Up Saldo** - Sistem saldo untuk pembelian
- **QR Code** - Generate QR code untuk mudah import
- **Link Konfigurasi** - Link untuk semua protokol
- **Status Server** - Cek status dan info server

### 👨‍💼 Fitur Admin
- **Panel Admin** - Dashboard lengkap untuk admin
- **Statistik** - Total user, akun, transaksi
- **Manajemen User** - Lihat semua user dan saldo
- **Manajemen Akun** - Lihat semua akun aktif
- **Broadcast** - Kirim pesan ke semua user

### 🔐 Protokol yang Didukung

#### VMess
- VMess WebSocket (WS)
- VMess WebSocket TLS (WS TLS)
- VMess TCP
- VMess gRPC

#### VLess
- VLess WebSocket (WS)
- VLess WebSocket TLS (WS TLS)
- VLess TCP TLS
- VLess gRPC

#### Trojan
- Trojan WebSocket (WS)
- Trojan WebSocket TLS (WS TLS)
- Trojan TCP TLS
- Trojan gRPC

## 🚀 Instalasi di VPS

### Persyaratan
- Ubuntu 20.04 / 22.04 atau Debian 10 / 11
- Minimal RAM 1GB
- Root access
- Domain (opsional, untuk SSL)

### Cara Install

1. **Login ke VPS sebagai root**
```bash
sudo su
```

2. **Clone repository atau upload files**
```bash
cd /root
mkdir vpn-bot
cd vpn-bot
# Upload semua file bot ke folder ini
```

3. **Jalankan installer**
```bash
chmod +x install.sh
./install.sh
```

4. **Installer akan meminta:**
   - Bot Token (dari @BotFather)
   - Admin ID (Telegram User ID Anda)
   - Domain name (opsional)
   - Server IP

5. **Tunggu instalasi selesai** (5-10 menit)

### Mendapatkan Bot Token

1. Buka Telegram, cari **@BotFather**
2. Kirim `/newbot`
3. Ikuti instruksi dan dapatkan token
4. Salin token untuk instalasi

### Mendapatkan User ID

1. Buka Telegram, cari **@userinfobot**
2. Kirim `/start`
3. Bot akan memberikan User ID Anda
4. Salin ID untuk instalasi

## 📝 Konfigurasi

### File Konfigurasi

#### `.env` - Environment Variables
```env
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=123456789,987654321
SERVER_DOMAIN=yourdomain.com
SERVER_IP=your_server_ip
DATABASE_URL=sqlite:///./vpn_bot.db
```

#### `config.json` - Bot Configuration
```json
{
  "telegram": {
    "bot_token": "YOUR_BOT_TOKEN",
    "admin_ids": [123456789]
  },
  "server": {
    "domain": "yourdomain.com",
    "ip": "YOUR_SERVER_IP"
  },
  "pricing": {
    "vmess_ws": 10000,
    "vless_ws": 12000,
    "trojan_ws": 15000
  }
}
```

### Mengubah Harga

Edit file `config.json` bagian `pricing`:
```json
"pricing": {
  "vmess_ws": 10000,        // Rp 10.000
  "vmess_ws_tls": 12000,    // Rp 12.000
  "vless_ws": 12000,
  "vless_ws_tls": 15000,
  "trojan_tcp_tls": 20000
}
```

Harga adalah untuk base price, akan dikalikan dengan:
- 7 hari: 0.7x
- 15 hari: 1.5x
- 30 hari: 3x
- 60 hari: 5x

## 🔧 Manajemen

### Perintah Systemd

```bash
# Cek status bot
systemctl status vpn-bot

# Start bot
systemctl start vpn-bot

# Stop bot
systemctl stop vpn-bot

# Restart bot
systemctl restart vpn-bot

# Lihat logs
journalctl -u vpn-bot -f

# Cek status Xray
systemctl status xray

# Restart Xray
systemctl restart xray
```

### Update Bot

```bash
cd /opt/vpn-bot
systemctl stop vpn-bot
# Upload file baru
systemctl start vpn-bot
```

### Backup Database

```bash
cp /opt/vpn-bot/vpn_bot.db /root/backup-$(date +%Y%m%d).db
```

## 📱 Cara Menggunakan Bot

### Untuk User

1. **Start Bot** - `/start`
2. **Beli Akun** - Pilih protokol dan durasi
3. **Lihat Akun** - Menu "Akun Saya"
4. **Dapatkan Link/QR** - Klik akun untuk detail
5. **Top Up** - Menu "Top Up Saldo"
6. **Trial** - Menu "Trial Gratis"

### Untuk Admin

1. **Akses Panel** - Menu "Panel Admin"
2. **Lihat Statistik** - Total user, akun, dll
3. **Kelola User** - Lihat semua user
4. **Approve Top Up** - Secara manual

## 🔐 Keamanan

### Firewall (UFW)

Port yang dibuka:
- 22 (SSH)
- 80 (HTTP)
- 443 (HTTPS)
- 8080 (VMess WS)
- 8443 (VMess WS TLS)
- 445 (Trojan WS TLS)
- 8081 (Trojan TCP)

### SSL Certificate

Bot otomatis generate SSL dengan:
1. Let's Encrypt (jika domain valid)
2. Self-signed (jika tidak ada domain)

Renew certificate:
```bash
certbot renew
systemctl restart xray
```

## 🗄️ Database

Bot menggunakan SQLite database: `vpn_bot.db`

### Tables
- **users** - Data user
- **vpn_accounts** - Akun VPN
- **transactions** - Transaksi
- **settings** - Pengaturan bot

## 📊 Monitoring

### Cek Logs

```bash
# Bot logs
journalctl -u vpn-bot -f

# Xray logs
journalctl -u xray -f

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Cek Resource

```bash
# CPU & RAM usage
htop

# Disk usage
df -h

# Network
nethogs
```

## 🐛 Troubleshooting

### Bot tidak start

```bash
# Cek logs
journalctl -u vpn-bot -n 50

# Cek Python
/opt/vpn-bot/venv/bin/python3 /opt/vpn-bot/bot.py

# Cek environment
cat /opt/vpn-bot/.env
```

### Xray tidak berfungsi

```bash
# Cek config
xray -test -config /usr/local/etc/xray/config.json

# Restart service
systemctl restart xray

# Cek logs
journalctl -u xray -n 50
```

### SSL Error

```bash
# Renew certificate
certbot renew --force-renewal

# Copy ke Xray
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /etc/xray/cert.crt
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /etc/xray/cert.key

# Restart Xray
systemctl restart xray
```

## 📞 Support

Untuk pertanyaan dan bantuan:
- Telegram: @youradmin
- Email: admin@yourdomain.com

## 📄 License

MIT License - Bebas digunakan dan dimodifikasi.

## 🙏 Credits

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Xray-core](https://github.com/XTLS/Xray-core)
- [SQLAlchemy](https://www.sqlalchemy.org/)

## 🔄 Updates

### Version 1.0.0
- ✅ Initial release
- ✅ Support VMess, VLess, Trojan
- ✅ Multiple protocols (WS, TCP, TLS)
- ✅ Trial system
- ✅ Admin panel
- ✅ QR code generation
- ✅ Auto installer

---

**Made with ❤️ for VPN sellers**
