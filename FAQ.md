# FAQ - Frequently Asked Questions

## 🤔 Pertanyaan Umum

### Q: Apa itu bot ini?
**A:** Bot Telegram untuk menjual akun VPN dengan berbagai protokol (VMess, VLess, Trojan). Bot ini terintegrasi dengan Xray-core untuk manajemen akun VPN secara otomatis.

### Q: Apakah bot ini gratis?
**A:** Ya, source code bot ini gratis. Anda hanya perlu membayar biaya VPS untuk hosting bot dan server VPN.

### Q: Berapa biaya VPS yang diperlukan?
**A:** Minimal $5-10/bulan untuk VPS dengan spec:
- RAM 1-2GB
- CPU 1-2 Core
- Bandwidth Unlimited atau 1TB+

Provider rekomendasi: DigitalOcean, Vultr, Linode, Contabo

### Q: Apakah perlu domain?
**A:** Tidak wajib, tapi sangat direkomendasikan untuk:
- SSL certificate gratis dari Let's Encrypt
- Lebih profesional
- Beberapa protokol TLS memerlukan domain

### Q: Apakah bot bisa digunakan tanpa Xray?
**A:** Tidak, bot ini didesain untuk bekerja dengan Xray-core. Xray adalah core VPN yang menangani koneksi client.

## 💰 Tentang Harga & Pembayaran

### Q: Bagaimana cara mengubah harga?
**A:** Edit file `/opt/vpn-bot/config.json` bagian `pricing`, lalu restart bot dengan `systemctl restart vpn-bot`.

### Q: Apakah ada sistem pembayaran otomatis?
**A:** Saat ini pembayaran manual (user transfer lalu konfirmasi ke admin). Anda bisa integrasikan payment gateway seperti:
- Midtrans
- Xendit
- Tripay
- Duitku

### Q: Bagaimana cara approve pembayaran?
**A:** Admin menambahkan saldo manual dengan command:
```bash
python3 manage.py add-balance TELEGRAM_USER_ID JUMLAH
```

### Q: Apakah bisa integrasi dengan payment gateway?
**A:** Ya, Anda perlu memodifikasi kode untuk integrasi API payment gateway. Dokumentasi payment gateway biasanya menyediakan tutorial.

## 🔐 Tentang Keamanan

### Q: Apakah bot ini aman?
**A:** Ya, selama Anda:
- Menggunakan SSL/TLS
- Update system secara rutin
- Jangan share Bot Token
- Gunakan password SSH yang kuat

### Q: Bagaimana cara backup data?
**A:** Database di-backup otomatis setiap hari via cron job ke `/opt/vpn-bot/backups/`. Atau manual:
```bash
cp /opt/vpn-bot/vpn_bot.db /root/backup.db
```

### Q: Apakah bisa di-hack?
**A:** Tidak ada sistem yang 100% aman. Tapi dengan konfigurasi yang benar (firewall, SSL, strong password), risiko sangat minimal.

## 👥 Tentang User & Akun

### Q: Berapa banyak user yang bisa dilayani?
**A:** Tergantung spec VPS. Rule of thumb:
- 1GB RAM: ~50-100 concurrent users
- 2GB RAM: ~100-200 concurrent users
- 4GB RAM: ~200-500 concurrent users

### Q: Apakah user bisa punya banyak akun?
**A:** Ya, user bisa beli beberapa akun dengan protokol berbeda.

### Q: Bagaimana cara delete akun user?
**A:** Via command:
```bash
python3 manage.py delete-account ACCOUNT_ID
```
Atau user bisa hapus sendiri via menu "Akun Saya".

### Q: Apakah ada sistem trial?
**A:** Ya, user bisa mendapatkan trial 1 jam gratis (1x per user).

### Q: Bagaimana cara disable trial?
**A:** Edit `config.json`:
```json
"trial": {
  "enabled": false,
  "duration_hours": 1
}
```

## 🚀 Tentang Protokol

### Q: Apa perbedaan VMess, VLess, dan Trojan?
**A:**
- **VMess**: Protocol matang, enkripsi built-in, sedikit lebih lambat
- **VLess**: Protocol ringan, lebih cepat, enkripsi via TLS
- **Trojan**: Menyamar sebagai HTTPS, bagus untuk bypass DPI

### Q: Mana yang paling cepat?
**A:** VLess TCP TLS umumnya tercepat, tapi tergantung network.

### Q: Mana yang paling aman?
**A:** Trojan dan VLess dengan TLS 1.3 paling aman.

### Q: Apakah support UDP?
**A:** Ya, semua protokol support UDP untuk gaming, video call, dll.

### Q: Bagaimana cara tambah protokol baru?
**A:** Edit `xray_manager.py` dan tambahkan inbound baru di Xray config.

## 🛠️ Troubleshooting

### Q: Bot tidak merespons, apa yang harus dilakukan?
**A:**
1. `systemctl status vpn-bot` - Cek status
2. `journalctl -u vpn-bot -n 50` - Lihat error
3. `systemctl restart vpn-bot` - Restart bot

### Q: Akun tidak bisa connect, kenapa?
**A:**
1. Cek status Xray: `systemctl status xray`
2. Test config: `xray -test -config /usr/local/etc/xray/config.json`
3. Cek port: `netstat -tulpn | grep xray`
4. Cek firewall: `ufw status`

### Q: SSL certificate expired, bagaimana renew?
**A:**
```bash
certbot renew
cp /etc/letsencrypt/live/DOMAIN/fullchain.pem /etc/xray/cert.crt
cp /etc/letsencrypt/live/DOMAIN/privkey.pem /etc/xray/cert.key
systemctl restart xray
```

### Q: VPS kehabisan resource, apa yang harus dilakukan?
**A:**
1. Upgrade VPS
2. Optimize: Hapus akun expired
3. Limit concurrent users
4. Gunakan CDN untuk static content

### Q: Error "Database is locked", kenapa?
**A:** SQLite tidak cocok untuk concurrent writes yang tinggi. Solusi:
1. Restart bot: `systemctl restart vpn-bot`
2. Upgrade ke PostgreSQL atau MySQL (perlu modifikasi code)

## 📱 Tentang Client Apps

### Q: Aplikasi apa yang digunakan user untuk connect?
**A:**
- **Android**: V2RayNG, SagerNet
- **iOS**: Shadowrocket, Quantumult X, V2Box
- **Windows**: V2RayN, Clash for Windows, Qv2ray
- **Mac**: V2RayU, ClashX, Qv2ray
- **Linux**: Qv2ray, V2Ray Desktop

### Q: Bagaimana cara import config?
**A:** User bisa:
1. Scan QR code
2. Copy-paste link
3. Import dari clipboard

### Q: Apakah support Clash?
**A:** Tidak langsung, tapi bisa convert config VMess/VLess ke format Clash.

## 💼 Tentang Bisnis

### Q: Berapa harga jual yang ideal?
**A:** Tergantung kompetitor dan kualitas. Umumnya:
- Trial: Gratis
- 7 hari: Rp 5.000 - 10.000
- 30 hari: Rp 15.000 - 30.000
- 60 hari: Rp 25.000 - 50.000

### Q: Bagaimana cara promosi?
**A:**
- Grup Telegram/WhatsApp
- Social media (Twitter, Facebook, Instagram)
- Forum online
- Paid ads (Google Ads, Facebook Ads)
- Referral program

### Q: Apakah legal menjual VPN?
**A:** Tergantung negara. Di Indonesia, VPN legal untuk digunakan. Pastikan tidak digunakan untuk aktivitas ilegal.

### Q: Berapa profit yang bisa didapat?
**A:** Contoh perhitungan:
- Biaya VPS: $10/bulan = Rp 150.000
- 30 user x Rp 20.000 = Rp 600.000
- Profit = Rp 450.000/bulan

Profit bisa lebih tinggi dengan lebih banyak user atau harga lebih tinggi.

### Q: Apakah bisa jadi passive income?
**A:** Ya, setelah setup awal, maintenance minimal. Tapi tetap perlu:
- Monitor server
- Customer support
- Update security

## 🔄 Update & Maintenance

### Q: Bagaimana cara update bot?
**A:**
1. Backup database
2. Stop bot: `systemctl stop vpn-bot`
3. Upload file baru
4. Start bot: `systemctl start vpn-bot`

### Q: Seberapa sering harus update?
**A:**
- System update: Mingguan
- Bot update: Saat ada fitur baru atau bug fix
- Xray update: Bulanan atau saat ada security update

### Q: Apakah ada auto update?
**A:** Tidak built-in. Anda perlu manual update untuk kontrol lebih baik.

### Q: Bagaimana cara rollback jika ada masalah?
**A:**
1. Stop bot
2. Restore backup database
3. Replace dengan file lama
4. Start bot

## 🌐 Lokasi Server & Performance

### Q: Dimana lokasi VPS yang bagus?
**A:** Tergantung target user:
- User Indonesia: Singapore, Malaysia, Jepang
- User Global: USA, UK, Jerman
- Multi-lokasi: Gunakan beberapa VPS

### Q: Bagaimana cara setup multi-server?
**A:** Install bot di setiap VPS atau gunakan 1 bot untuk kontrol beberapa Xray server (perlu custom code).

### Q: Apakah bisa gunakan CDN?
**A:** Ya, CDN seperti Cloudflare bisa digunakan untuk protocol WebSocket.

### Q: Bagaimana cara monitoring performance?
**A:**
- `htop` - CPU & RAM
- `iftop` - Network bandwidth
- `df -h` - Disk usage
- Xray stats API - Traffic per user

## 📞 Support

### Q: Dimana bisa bertanya jika ada masalah?
**A:**
- Baca dokumentasi lengkap di README.md
- Cek INSTALLATION_ID.md untuk panduan Indonesia
- Lihat logs untuk error message
- Hubungi developer/komunitas

### Q: Apakah ada komunitas pengguna?
**A:** Anda bisa bergabung dengan komunitas VPN di Telegram, Reddit, atau forum lokal.

### Q: Apakah ada support berbayar?
**A:** Tergantung developer. Beberapa menawarkan:
- Setup service
- Customization
- Technical support
- Training

---

**Tidak menemukan jawaban?**
Silakan cek dokumentasi lengkap atau hubungi support.
