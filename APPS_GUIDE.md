# Panduan Aplikasi Client VPN

Panduan untuk user dalam menggunakan akun VPN yang dibeli dari bot.

## 📱 Aplikasi Android

### V2RayNG (Rekomendasi)
**Download:** [Google Play Store](https://play.google.com/store/apps/details?id=com.v2ray.ang) atau [GitHub](https://github.com/2dust/v2rayNG/releases)

**Cara Pakai:**
1. Install aplikasi V2RayNG
2. Buka aplikasi
3. Klik tombol "+" di kanan atas
4. Pilih "Import config from clipboard" atau "Scan QR code"
5. Paste link atau scan QR dari bot
6. Klik akun yang baru ditambahkan
7. Klik tombol pesawat di bawah untuk connect

**Support:** VMess, VLess, Trojan, Shadowsocks, Socks

### SagerNet
**Download:** [GitHub](https://github.com/SagerNet/SagerNet/releases)

**Kelebihan:**
- Open source
- Support banyak protocol
- Custom routing

**Cara Pakai:** Sama dengan V2RayNG

---

## 🍎 Aplikasi iOS

### Shadowrocket (Berbayar $2.99)
**Download:** [App Store](https://apps.apple.com/app/shadowrocket/id932747118)

**Cara Pakai:**
1. Install Shadowrocket
2. Buka aplikasi
3. Klik "+" di kanan atas
4. Pilih "QR Code" atau "Paste from Clipboard"
5. Scan QR atau paste link
6. Toggle switch untuk connect

**Support:** VMess, VLess, Trojan, Shadowsocks, Socks

### Quantumult X (Berbayar $7.99)
**Download:** [App Store](https://apps.apple.com/app/quantumult-x/id1443988620)

**Kelebihan:**
- Powerful rules
- Custom script support
- Advanced features

### V2Box (Gratis)
**Download:** [App Store](https://apps.apple.com/app/v2box/id1540039663)

**Note:** Gratis tapi dengan ads dan limited features.

---

## 💻 Aplikasi Windows

### V2RayN (Rekomendasi)
**Download:** [GitHub](https://github.com/2dust/v2rayN/releases)

**Cara Pakai:**
1. Download dan extract V2RayN
2. Jalankan v2rayN.exe (tidak perlu install)
3. Klik kanan icon di system tray
4. "Import bulk URL from clipboard" atau "Import from QR code"
5. Paste link atau scan QR
6. Klik kanan server → "Set as active server"
7. Klik "HTTP Proxy" → "Enable"

**Support:** VMess, VLess, Trojan, Shadowsocks, Socks

### Clash for Windows
**Download:** [GitHub](https://github.com/Fndroid/clash_for_windows_pkg/releases)

**Kelebihan:**
- Beautiful UI
- Rule-based routing
- Support Clash config

**Cara Pakai:**
1. Install Clash for Windows
2. Convert VMess/VLess link ke Clash config
3. Import config file
4. Enable "System Proxy"

### Qv2ray
**Download:** [GitHub](https://github.com/Qv2ray/Qv2ray/releases)

**Kelebihan:**
- Cross-platform
- Plugin support
- Advanced routing

---

## 🍏 Aplikasi macOS

### V2RayU
**Download:** [GitHub](https://github.com/yanue/V2rayU/releases)

**Cara Pakai:**
1. Install V2RayU
2. Buka aplikasi (icon di menu bar)
3. "Import" → "Import from clipboard"
4. Paste link dari bot
5. Klik "Turn on" untuk connect

### ClashX
**Download:** [GitHub](https://github.com/yichengchen/clashX/releases)

**Kelebihan:**
- Native macOS app
- Rule-based proxy
- Auto update

### Qv2ray
**Download:** [GitHub](https://github.com/Qv2ray/Qv2ray/releases)

Cross-platform, sama dengan Windows version.

---

## 🐧 Aplikasi Linux

### Qv2ray
**Download:** [GitHub](https://github.com/Qv2ray/Qv2ray/releases)

**Install (Ubuntu/Debian):**
```bash
# Download AppImage
chmod +x Qv2ray.AppImage
./Qv2ray.AppImage
```

### V2Ray Desktop
**Download:** [GitHub](https://github.com/Dr-Incognito/V2Ray-Desktop/releases)

### Command Line (Advanced)
```bash
# Install Xray-core
bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install

# Create config file
nano config.json
# Paste config atau convert dari link

# Run Xray
xray -config config.json
```

---

## 🎮 Setup untuk Gaming

### Windows
1. Install V2RayN
2. Enable "HTTP Proxy" mode
3. Set system proxy ke `127.0.0.1:10809`
4. Game akan otomatis menggunakan VPN

### Android
1. Install V2RayNG
2. Enable VPN mode (bukan proxy mode)
3. All traffic including games akan lewat VPN

### Game Console (PS4/Xbox)
1. Setup VPN di router/PC
2. Share koneksi VPN ke console
3. Or use PC as proxy gateway

---

## 📺 Setup untuk Streaming

### Netflix, Disney+, dll
1. Connect VPN dengan server US/UK
2. Clear browser cache/app data
3. Restart aplikasi streaming
4. Enjoy!

**Tips:**
- Gunakan VLess TCP atau Trojan TCP untuk streaming (lebih stabil)
- Jika buffering, coba ganti server

---

## ⚙️ Settings Rekomendasi

### Untuk Speed
- **Protocol:** VLess TCP TLS
- **Mode:** Direct/Global
- **DNS:** 1.1.1.1, 8.8.8.8

### Untuk Bypass Firewall
- **Protocol:** VMess/VLess WebSocket TLS
- **Mode:** Rule-based
- **CDN:** Enable jika tersedia

### Untuk Gaming
- **Protocol:** VLess TCP atau Trojan TCP
- **Mode:** Game mode/Low latency
- **UDP:** Enable

### Untuk Streaming
- **Protocol:** Trojan TCP TLS
- **Mode:** Global proxy
- **Buffer:** Large

---

## 🔧 Troubleshooting

### Tidak bisa connect
1. ✅ Pastikan link/QR benar
2. ✅ Cek koneksi internet
3. ✅ Coba restart aplikasi
4. ✅ Cek apakah akun expired
5. ✅ Hubungi admin

### Connect tapi tidak bisa browsing
1. ✅ Cek DNS settings
2. ✅ Clear cache browser
3. ✅ Coba mode Global instead of Rule
4. ✅ Restart device

### Speed lambat
1. ✅ Coba ganti protocol (TCP lebih cepat dari WS)
2. ✅ Tutup aplikasi lain yang pakai bandwidth
3. ✅ Cek apakah server sedang penuh
4. ✅ Contact admin untuk info server

### Disconnect sendiri
1. ✅ Cek koneksi internet stabil
2. ✅ Coba protocol lain
3. ✅ Update aplikasi ke versi terbaru
4. ✅ Hubungi admin

---

## 💡 Tips & Tricks

### Hemat Kuota
- Gunakan split tunneling (hanya app tertentu lewat VPN)
- Disable auto-update saat VPN aktif
- Gunakan Lite mode di aplikasi

### Maksimalkan Speed
- Pilih server terdekat
- Gunakan TCP instead of WebSocket
- Enable hardware acceleration di app
- Close background apps

### Keamanan Maksimal
- Always use TLS version
- Enable kill switch di app
- Use DNS over HTTPS
- Don't save sensitive password saat VPN aktif

### Multi-Device
- 1 akun biasanya bisa untuk 2-3 device
- Jangan share akun ke terlalu banyak device
- Beli akun terpisah jika perlu banyak device

---

## 📞 Need Help?

Jika masih ada masalah:
1. Screenshot error message
2. Note: Aplikasi apa, OS apa, protocol apa
3. Hubungi admin via bot: Menu → Hubungi Admin
4. Admin akan bantu troubleshoot

---

## 🌟 Best Practices

✅ **DO:**
- Update app regularly
- Test different protocols untuk cari yang paling cocok
- Report jika ada masalah ke admin
- Renew sebelum akun expired

❌ **DON'T:**
- Share akun ke banyak orang (bisa overload)
- Download/upload file ilegal
- Spam atau flood network
- Gunakan untuk aktivitas ilegal

---

**Enjoy your VPN service! 🚀**
