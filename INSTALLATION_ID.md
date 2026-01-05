# Panduan Instalasi Bot Telegram VPN (Bahasa Indonesia)

## 📋 Persiapan

### 1. Persyaratan VPS
- **OS**: Ubuntu 20.04/22.04 atau Debian 10/11
- **RAM**: Minimal 1GB (Rekomendasi 2GB)
- **Storage**: Minimal 10GB
- **CPU**: 1 Core (Rekomendasi 2 Core)
- **Bandwidth**: Unlimited atau minimal 1TB/bulan

### 2. Dapatkan Bot Token
1. Buka Telegram, cari **@BotFather**
2. Kirim `/newbot`
3. Masukkan nama bot (contoh: `VPN Store Bot`)
4. Masukkan username bot (contoh: `myvpnstore_bot`)
5. Salin token yang diberikan (format: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

### 3. Dapatkan User ID Telegram Anda
1. Buka Telegram, cari **@userinfobot**
2. Kirim `/start`
3. Salin User ID yang diberikan (contoh: `123456789`)

### 4. Domain (Opsional tapi Direkomendasikan)
- Beli domain dari provider seperti Namecheap, GoDaddy, dll
- Arahkan DNS A Record ke IP VPS Anda
- Tunggu propagasi DNS (5-30 menit)

## 🚀 Instalasi Otomatis

### Langkah 1: Login ke VPS
```bash
ssh root@IP_VPS_ANDA
```

### Langkah 2: Download Files
```bash
# Clone repository atau upload files
cd /root
mkdir vpn-bot
cd vpn-bot

# Upload semua file bot ke folder ini
# Atau gunakan git jika ada repository
# git clone https://github.com/username/vpn-bot.git .
```

### Langkah 3: Jalankan Installer
```bash
chmod +x install.sh
./install.sh
```

### Langkah 4: Isi Informasi
Installer akan meminta:
1. **Bot Token**: Paste token dari BotFather
2. **Admin ID**: Paste User ID Anda
3. **Domain**: Masukkan domain Anda (atau tekan Enter untuk skip)
4. **Server IP**: Masukkan IP VPS Anda

### Langkah 5: Tunggu Instalasi
Proses instalasi memakan waktu 5-15 menit tergantung koneksi internet.

## ✅ Verifikasi Instalasi

### Cek Status Bot
```bash
systemctl status vpn-bot
```
Harus menunjukkan status **active (running)** berwarna hijau.

### Cek Status Xray
```bash
systemctl status xray
```
Harus menunjukkan status **active (running)** berwarna hijau.

### Cek Logs Bot
```bash
journalctl -u vpn-bot -f
```
Tekan `Ctrl+C` untuk keluar.

### Test Bot di Telegram
1. Buka Telegram
2. Cari bot Anda berdasarkan username
3. Kirim `/start`
4. Bot harus merespons dengan menu utama

## ⚙️ Konfigurasi Lanjutan

### Mengubah Harga
Edit file `/opt/vpn-bot/config.json`:
```bash
nano /opt/vpn-bot/config.json
```

Ubah bagian pricing:
```json
"pricing": {
  "vmess_ws": 10000,        // Rp 10.000
  "vmess_ws_tls": 12000,    // Rp 12.000
  "vless_ws": 12000,
  "vless_ws_tls": 15000,
  "vless_tcp_tls": 18000,
  "trojan_ws": 15000,
  "trojan_ws_tls": 18000,
  "trojan_tcp_tls": 20000
}
```

Restart bot:
```bash
systemctl restart vpn-bot
```

### Menambah Admin Baru
```bash
cd /opt/vpn-bot
source venv/bin/activate
python3 manage.py add-admin TELEGRAM_USER_ID
```

### Menambah Saldo User (Manual)
```bash
cd /opt/vpn-bot
source venv/bin/activate
python3 manage.py add-balance TELEGRAM_USER_ID JUMLAH
```

Contoh: Tambah Rp 50.000 ke user 123456789
```bash
python3 manage.py add-balance 123456789 50000
```

### Lihat Semua User
```bash
cd /opt/vpn-bot
source venv/bin/activate
python3 manage.py list-users
```

### Lihat Semua Akun Aktif
```bash
cd /opt/vpn-bot
source venv/bin/activate
python3 manage.py list-accounts
```

### Lihat Statistik
```bash
cd /opt/vpn-bot
source venv/bin/activate
python3 manage.py stats
```

## 🔧 Troubleshooting

### Bot tidak merespons
1. Cek status bot:
   ```bash
   systemctl status vpn-bot
   ```

2. Cek logs untuk error:
   ```bash
   journalctl -u vpn-bot -n 50
   ```

3. Restart bot:
   ```bash
   systemctl restart vpn-bot
   ```

### Akun tidak bisa connect
1. Cek status Xray:
   ```bash
   systemctl status xray
   ```

2. Test konfigurasi Xray:
   ```bash
   xray -test -config /usr/local/etc/xray/config.json
   ```

3. Cek port yang terbuka:
   ```bash
   netstat -tulpn | grep xray
   ```

4. Restart Xray:
   ```bash
   systemctl restart xray
   ```

### Port tidak terbuka
1. Cek firewall:
   ```bash
   ufw status
   ```

2. Buka port yang diperlukan:
   ```bash
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw allow 8080/tcp
   ufw allow 8443/tcp
   ufw allow 445/tcp
   ufw allow 8081/tcp
   ```

### SSL Certificate Error
1. Renew certificate:
   ```bash
   certbot renew --force-renewal
   ```

2. Copy ke Xray:
   ```bash
   cp /etc/letsencrypt/live/DOMAIN/fullchain.pem /etc/xray/cert.crt
   cp /etc/letsencrypt/live/DOMAIN/privkey.pem /etc/xray/cert.key
   ```

3. Restart Xray:
   ```bash
   systemctl restart xray
   ```

## 📊 Monitoring

### Cek Resource VPS
```bash
# CPU & RAM
htop

# Disk space
df -h

# Network
nethogs
```

### Logs Penting
```bash
# Bot logs
tail -f /var/log/syslog | grep vpn-bot

# Xray logs
journalctl -u xray -f

# Nginx logs (jika ada)
tail -f /var/log/nginx/error.log
```

## 🔄 Update Bot

### Update Code
```bash
cd /opt/vpn-bot
systemctl stop vpn-bot

# Backup database
cp vpn_bot.db vpn_bot.db.backup

# Update files (upload file baru atau git pull)
# ...

# Restart bot
systemctl start vpn-bot
```

## 🗑️ Uninstall

### Hapus Bot
```bash
systemctl stop vpn-bot
systemctl disable vpn-bot
rm /etc/systemd/system/vpn-bot.service
rm -rf /opt/vpn-bot
systemctl daemon-reload
```

### Hapus Xray (Opsional)
```bash
bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ remove
```

## 📞 Support

Jika mengalami masalah:
1. Cek dokumentasi di README.md
2. Cek logs error
3. Hubungi developer/admin

## 💡 Tips

1. **Backup Rutin**: Backup database setiap hari
   ```bash
   cp /opt/vpn-bot/vpn_bot.db /root/backup-$(date +%Y%m%d).db
   ```

2. **Monitor Resource**: Pastikan VPS tidak overload
   ```bash
   htop
   ```

3. **Update Security**: Update system secara rutin
   ```bash
   apt update && apt upgrade -y
   ```

4. **Gunakan Domain**: Lebih profesional dan SSL gratis

5. **Set Harga Wajar**: Sesuaikan dengan kompetitor

6. **Layanan Customer**: Respons cepat untuk kepuasan pelanggan

## 🎉 Selamat!

Bot Telegram VPN Anda sudah siap digunakan!
Mulai promosikan bot Anda dan dapatkan customer!
