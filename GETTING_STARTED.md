# 🚀 Getting Started - Bot Telegram VPN

Panduan cepat untuk memulai bot Telegram VPN Anda!

---

## 📋 Prerequisites

Sebelum memulai, pastikan Anda memiliki:

1. ✅ **VPS/Server** 
   - Ubuntu 20.04/22.04 atau Debian 10/11
   - Min. 1GB RAM, 1 CPU Core, 10GB Storage
   - Root access

2. ✅ **Telegram Bot Token**
   - Buka [@BotFather](https://t.me/BotFather) di Telegram
   - Kirim `/newbot` dan ikuti instruksi
   - Salin token yang diberikan

3. ✅ **Telegram User ID**
   - Buka [@userinfobot](https://t.me/userinfobot)
   - Kirim `/start`
   - Salin User ID Anda

4. ✅ **Domain** (Opsional)
   - Domain untuk SSL certificate
   - Arahkan A Record ke IP VPS

---

## ⚡ Quick Install (3 Steps)

### Step 1: Upload Files ke VPS
```bash
# Login ke VPS
ssh root@YOUR_VPS_IP

# Buat direktori
mkdir -p /root/vpn-bot
cd /root/vpn-bot

# Upload semua file ke folder ini
# Menggunakan SCP, FTP, atau Git
```

### Step 2: Run Installer
```bash
# Jalankan installer
chmod +x install.sh
./install.sh
```

### Step 3: Input Konfigurasi
Installer akan meminta:
- **Bot Token**: Paste token dari BotFather
- **Admin ID**: Paste User ID Anda
- **Domain**: Domain Anda (tekan Enter jika tidak ada)
- **Server IP**: IP VPS Anda

**Tunggu 5-15 menit** sampai instalasi selesai.

---

## ✅ Verify Installation

### 1. Check Services
```bash
# Check bot status
systemctl status vpn-bot

# Check Xray status
systemctl status xray
```

Kedua service harus menunjukkan **active (running)** dengan warna hijau.

### 2. Check Logs
```bash
# View bot logs
journalctl -u vpn-bot -f
```

Tekan `Ctrl+C` untuk keluar.

### 3. Test Bot
1. Buka Telegram
2. Cari bot Anda (username yang dibuat di BotFather)
3. Kirim `/start`
4. Bot harus merespons dengan menu utama

---

## 🎯 First Time Setup

### 1. Verify Admin Access
```bash
cd /opt/vpn-bot
source venv/bin/activate
python3 manage.py add-admin YOUR_TELEGRAM_ID
```

### 2. Customize Pricing
Edit harga sesuai keinginan:
```bash
nano /opt/vpn-bot/config.json
```

Ubah bagian `pricing`, contoh:
```json
"pricing": {
  "vmess_ws": 10000,
  "vless_ws_tls": 15000,
  "trojan_tcp_tls": 20000
}
```

Save dengan `Ctrl+O`, Enter, lalu `Ctrl+X`.

### 3. Restart Bot
```bash
systemctl restart vpn-bot
```

### 4. Setup Cron Jobs (Optional)
```bash
cd /opt/vpn-bot
./setup_cron.sh
```

---

## 🎮 Using the Bot

### As User
1. **/start** - Mulai bot dan registrasi
2. **🛒 Beli Akun** - Pilih protocol dan durasi
3. **👤 Akun Saya** - Lihat akun yang dimiliki
4. **💰 Top Up Saldo** - Top up untuk beli akun
5. **🎁 Trial Gratis** - Dapatkan trial 1 jam
6. **📊 Status Server** - Cek status server

### As Admin
1. **⚙️ Panel Admin** - Akses panel admin
2. View statistik user dan akun
3. Approve top up (manual)
4. Broadcast pesan ke user

---

## 💰 Payment Flow

### User Perspective
1. User pilih "💰 Top Up Saldo"
2. Pilih nominal (10k, 25k, 50k, dll)
3. Bot kirim info rekening bank/e-wallet
4. User transfer dan kirim bukti ke admin
5. Admin approve dan saldo masuk
6. User bisa beli akun VPN

### Admin Perspective
1. User konfirmasi pembayaran
2. Admin cek transfer
3. Admin tambah saldo manual:
```bash
python3 manage.py add-balance TELEGRAM_ID AMOUNT
```

---

## 📊 Daily Operations

### Check System Health
```bash
./check_system.sh
```

### View Statistics
```bash
cd /opt/vpn-bot
source venv/bin/activate
python3 manage.py stats
```

### List All Users
```bash
python3 manage.py list-users
```

### List Active Accounts
```bash
python3 manage.py list-accounts
```

### Backup Database
```bash
./backup.sh
```

---

## 🔧 Common Tasks

### Add Balance to User
```bash
cd /opt/vpn-bot
source venv/bin/activate
python3 manage.py add-balance TELEGRAM_ID AMOUNT
```

Example:
```bash
python3 manage.py add-balance 123456789 50000
```

### Make Someone Admin
```bash
python3 manage.py add-admin TELEGRAM_ID
```

### Delete Expired Accounts
```bash
python3 manage.py cleanup
```

### Restart Services
```bash
systemctl restart vpn-bot
systemctl restart xray
```

---

## 🐛 Troubleshooting

### Bot Tidak Merespons
```bash
# Check status
systemctl status vpn-bot

# View logs
journalctl -u vpn-bot -n 50

# Restart
systemctl restart vpn-bot
```

### Akun Tidak Bisa Connect
```bash
# Check Xray
systemctl status xray

# Test config
xray -test -config /usr/local/etc/xray/config.json

# Restart
systemctl restart xray
```

### Port Tidak Terbuka
```bash
# Check firewall
ufw status

# Allow ports
ufw allow 80,443,8080,8443,445,8081/tcp
```

---

## 📚 Next Steps

1. **Customize Bot Messages** - Edit `bot.py` untuk ubah pesan
2. **Setup Payment Gateway** - Integrasi Midtrans/Xendit
3. **Add More Servers** - Deploy di multiple locations
4. **Marketing** - Promosi bot Anda
5. **Monitor** - Gunakan `./monitor.sh` untuk monitoring real-time

---

## 📖 Documentation

- **README.md** - Dokumentasi lengkap
- **INSTALLATION_ID.md** - Panduan instalasi Bahasa Indonesia
- **FAQ.md** - Pertanyaan umum
- **APPS_GUIDE.md** - Panduan aplikasi client
- **QUICK_REFERENCE.md** - Referensi command
- **PROJECT_SUMMARY.md** - Summary project

---

## 💡 Pro Tips

1. **Use Domain** - Lebih profesional dan SSL gratis
2. **Regular Backup** - Backup database setiap hari
3. **Monitor Resources** - Pastikan VPS tidak overload
4. **Update Regularly** - Update system dan Xray
5. **Good Support** - Respons cepat = customer happy
6. **Fair Pricing** - Riset harga kompetitor
7. **Quality Server** - Speed dan stability penting
8. **Clear Instructions** - Panduan lengkap untuk user

---

## 🎉 Success!

Bot Telegram VPN Anda sudah siap digunakan!

**Next:** Mulai promosikan bot dan dapatkan customer pertama! 🚀

---

**Need Help?**
- Read documentation in README.md
- Check FAQ.md for common questions
- Review logs: `journalctl -u vpn-bot -f`

---

**Good luck with your VPN business!** 💰
