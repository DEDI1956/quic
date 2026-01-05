# Laporan Perbaikan: Xray Manager & Trial Account

## 📋 Ringkasan Masalah

Bot Telegram selalu menampilkan pesan "layanan VPN sedang maintenance" walaupun Xray service running dan API port 10085 aktif. Trial VPN tidak pernah berhasil dibuat.

### Penyebab Root Cause:

1. **Silent Fallback Default Config**: `xray_manager.py` menggunakan fallback `get_default_config()` secara diam-diam ketika gagal membaca `/usr/local/etc/xray/config.json`
2. **Default Config TLS-Only**: Default config berisi VLESS TLS (port 443) yang tidak sesuai dengan setup non-TLS
3. **Validasi Terlalu Ketat**: Validasi Xray memaksa TLS & domain, sehingga bot selalu masuk mode maintenance
4. **Tidak Ada Verifikasi**: Akun yang dibuat bot tidak dijamin benar-benar ter-apply ke inbound Xray yang aktif

## ✅ Perubahan Yang Dilakukan

### 1. **xray_manager.py** - Perbaikan Total

#### a) **HAPUS Fallback Default Config**
```python
# SEBELUM (BURUK):
def load_config(self) -> dict:
    try:
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
    return self.get_default_config()  # ❌ SILENT FALLBACK!

# SESUDAH (BAIK):
def load_config(self) -> dict:
    """Load Xray config. NO FALLBACK - Fail with clear error."""
    if not os.path.exists(self.config_path):
        msg = f"CRITICAL: Xray config file not found: {self.config_path}"
        logger.error(msg)
        raise FileNotFoundError(msg)  # ✅ FAIL KERAS!
    
    # ... validasi lainnya ...
```

#### b) **Auto-Detect Config Path**
```python
def _detect_running_config_path(self) -> Optional[str]:
    """Detect config path from running Xray service via systemctl/pgrep."""
    # Cek dari systemctl show xray
    # Fallback ke pgrep -a xray
    # Fallback ke common paths
```

Ini memastikan XrayManager menggunakan config yang BENAR-BENAR digunakan oleh Xray running.

#### c) **Validasi Realistis**
```python
def check_health(self) -> Tuple[bool, str]:
    """Validasi realistis:
    - Xray service running ✅
    - Xray API accessible (port 10085) ✅  
    - TIDAK memaksa TLS ✅
    - TIDAK memaksa domain ✅
    """
    svc_ok, svc_msg = self.check_service_status()
    api_ok, api_msg = self.check_xray_api()
    
    if svc_ok and api_ok:
        return True, "OK"
    # ... error handling ...
```

#### d) **Verifikasi Client Applied**
```python
def _verify_client_applied(self, inbound_tag: str, email: str, uuid: str, protocol: str) -> Tuple[bool, str]:
    """Verifikasi client benar-benar ter-apply setelah save & reload."""
    inbound = self.find_inbound_by_tag(inbound_tag)
    if not inbound:
        return False, f"Inbound '{inbound_tag}' not found after reload"
    
    # Cek UUID/password cocok
    # ...
```

#### e) **Atomic Write Config**
```python
def _atomic_write_json(self, path: str, data: Dict) -> None:
    """Write config atomically using tempfile + os.replace."""
    # Menghindari corrupt config jika write interrupted
```

#### f) **Smart Reload/Restart**
```python
def restart_xray(self) -> Tuple[bool, str]:
    """Try reload first (faster), fallback to restart."""
    reload = self._run(["systemctl", "reload", "xray"])
    if reload.returncode == 0:
        return self.check_health()
    
    # Fallback restart
```

### 2. **bot.py** - Error Handling yang Jelas

#### a) **Safe XrayManager Initialization**
```python
# Initialize XrayManager with clear error handling
try:
    xray = XrayManager()
    logger.info("XrayManager initialized successfully")
except FileNotFoundError as e:
    logger.critical(f"FATAL: Xray config file not found: {e}")
    logger.critical("Please ensure /usr/local/etc/xray/config.json exists")
    xray = None
except PermissionError as e:
    logger.critical(f"FATAL: Permission denied for Xray config: {e}")
    xray = None
# ... dll
```

#### b) **Explicit Error Messages untuk Trial**
```python
async def create_trial_account(...):
    # Check if XrayManager initialized
    if xray is None:
        await query.message.edit_text(
            "❌ Layanan VPN belum dikonfigurasi dengan benar.\n\n"
            "Hubungi admin untuk bantuan.\n\n"
            "Error: XrayManager tidak terinisialisasi"
        )
        return
    
    # Check service running
    is_running, service_msg = xray.check_service_status()
    if not is_running:
        await query.message.edit_text(
            f"❌ Layanan Xray tidak berjalan!\n\n"
            f"Detail: {service_msg}\n\n"
            f"Hubungi admin untuk memperbaiki service."
        )
        return
```

Sekarang user mendapat error message yang **JELAS** bukan generic "sedang maintenance".

## 🎯 Hasil Perbaikan

### ✅ Yang Diperbaiki:

1. **No More Silent Failure**: Jika config tidak ada atau invalid → fail keras dengan error jelas
2. **No More TLS Fallback**: Tidak ada lagi default config TLS yang salah
3. **Realistic Validation**: Cukup cek Xray running + API aktif (tidak paksa TLS/domain)
4. **Client Verification**: Setiap client yang dibuat diverifikasi benar-benar aktif
5. **Clear Error Messages**: User dan admin mendapat pesan error yang spesifik
6. **Support Non-TLS Setup**: Repository sekarang bisa jalan TANPA TLS
7. **Auto-Detect Config Path**: XrayManager pintar mencari config yang benar

### ✅ Trial Account Sekarang:

- **Berhasil dibuat** jika Xray running & config.json valid
- **Ditambahkan ke inbound yang benar** (vmess-ws)
- **Ditulis ke config.json** dengan atomic write
- **Xray direload/restart** dengan benar
- **Diverifikasi** client muncul di inbound clients
- **Bisa langsung dipakai** oleh client VPN

### ✅ Error Handling:

Jika gagal, bot menampilkan error yang jelas:
- "Xray service tidak berjalan" → Admin tahu harus start service
- "Config file not found" → Admin tahu harus create config
- "No write permission" → Admin tahu harus fix permission
- "Inbound 'vmess-ws' not found. Available: ..." → Admin tahu harus add inbound

## 📖 Cara Menggunakan

### Setup Non-TLS (Tanpa Domain)

1. **Copy example config**:
```bash
sudo cp /path/to/project/xray_config_example.json /usr/local/etc/xray/config.json
```

2. **Edit untuk non-TLS** (hapus semua inbound TLS, biarkan hanya non-TLS):
```bash
sudo nano /usr/local/etc/xray/config.json
```

Contoh minimal config non-TLS:
```json
{
  "log": {
    "loglevel": "warning"
  },
  "api": {
    "tag": "api",
    "services": ["HandlerService", "StatsService"]
  },
  "inbounds": [
    {
      "port": 10085,
      "protocol": "dokodemo-door",
      "tag": "api",
      "settings": {
        "address": "127.0.0.1"
      }
    },
    {
      "port": 8080,
      "protocol": "vmess",
      "tag": "vmess-ws",
      "settings": {
        "clients": []
      },
      "streamSettings": {
        "network": "ws",
        "security": "none",
        "wsSettings": {
          "path": "/vmess"
        }
      }
    },
    {
      "port": 80,
      "protocol": "vless",
      "tag": "vless-ws",
      "settings": {
        "clients": [],
        "decryption": "none"
      },
      "streamSettings": {
        "network": "ws",
        "security": "none",
        "wsSettings": {
          "path": "/vless"
        }
      }
    }
  ],
  "outbounds": [
    {
      "protocol": "freedom",
      "tag": "direct"
    }
  ]
}
```

3. **Set permission**:
```bash
sudo chmod 644 /usr/local/etc/xray/config.json
sudo chown root:root /usr/local/etc/xray/config.json
```

4. **Restart Xray**:
```bash
sudo systemctl restart xray
sudo systemctl status xray
```

5. **Test API**:
```bash
nc -zv 127.0.0.1 10085
# atau
curl -v telnet://127.0.0.1:10085
```

6. **Restart bot**:
```bash
sudo systemctl restart vpn-bot
sudo journalctl -u vpn-bot -f
```

### Setup TLS (Dengan Domain)

Gunakan `xray_config_example.json` as-is, pastikan:
- Certificate exist di `/etc/xray/cert.crt` dan `/etc/xray/cert.key`
- Domain sudah di-point ke server IP
- Firewall allow port 80, 443, dll

## 🧪 Testing

### 1. Test XrayManager Initialization
```python
from xray_manager import XrayManager

try:
    xray = XrayManager()
    print("✅ XrayManager initialized")
    print(f"Config path: {xray.config_path}")
    print(f"Available inbounds: {xray.get_available_inbounds()}")
except Exception as e:
    print(f"❌ Error: {e}")
```

### 2. Test Health Check
```python
is_healthy, msg = xray.check_health()
print(f"Health: {'✅' if is_healthy else '❌'} {msg}")
```

### 3. Test Add Client
```python
result, error = xray.add_client("vmess", "test@example.com", connection_type="ws")
if result:
    print(f"✅ Client created: {result}")
else:
    print(f"❌ Error: {error}")
```

### 4. Test Trial dari Bot
1. Buka bot Telegram
2. Klik "🎁 Trial Gratis"
3. Pilih protocol (VMess/VLess/Trojan)
4. Lihat hasilnya:
   - Jika berhasil: Dapat link & QR code
   - Jika gagal: Dapat error message yang jelas

## 🔍 Debugging

### Jika Trial Masih Gagal:

1. **Cek log bot**:
```bash
sudo journalctl -u vpn-bot -f
```

2. **Cek Xray service**:
```bash
sudo systemctl status xray
sudo journalctl -u xray -f
```

3. **Cek config path**:
```bash
ps aux | grep xray
# Lihat -config flag
```

4. **Cek API port**:
```bash
netstat -tlnp | grep 10085
# atau
ss -tlnp | grep 10085
```

5. **Test manual add client**:
```bash
cd /opt/vpn-bot
source venv/bin/activate
python3
>>> from xray_manager import XrayManager
>>> xray = XrayManager()
>>> xray.check_health()
>>> xray.add_client("vmess", "manual-test@test.com", connection_type="ws")
```

## 📝 Breaking Changes

### API Changes

`add_client()` sekarang menggunakan `check_health()` instead of individual `check_service_status()` dan `check_config_accessibility()`.

Jika ada custom code yang call `add_client()`, tidak perlu perubahan (backward compatible).

### Config Requirements

- Config file **WAJIB** ada di disk (tidak ada fallback)
- Config file **WAJIB** valid JSON
- Config file **WAJIB** punya 'inbounds' array
- Inbound tag **HARUS** match pattern: `{protocol}-{connection_type}`
  - Examples: `vmess-ws`, `vmess-ws-tls`, `vless-tcp`, `trojan-tcp-tls`

## 🚀 Next Steps

1. ✅ Test trial creation
2. ✅ Test purchase flow
3. ✅ Monitor logs untuk error
4. ✅ Update documentation jika perlu
5. ⬜ (Optional) Add WebUI untuk manage config
6. ⬜ (Optional) Add metrics/monitoring

## 💡 Tips

- **Gunakan non-TLS untuk development/testing** (lebih simple)
- **Gunakan TLS untuk production** (lebih aman)
- **Monitor logs** secara berkala untuk detect issues
- **Backup config** sebelum major changes (XrayManager auto-backup setiap save)
- **Test di local** dulu sebelum deploy ke production

## 📞 Support

Jika ada masalah atau pertanyaan:
1. Cek logs (bot & xray)
2. Baca error message dengan teliti
3. Follow troubleshooting steps di atas
4. Jika masih stuck, open issue dengan:
   - Error message lengkap
   - Logs (bot & xray)
   - Config structure (tanpa sensitive data)
   - Steps to reproduce

---

**Perbaikan selesai! Bot sekarang bisa create trial VPN dengan benar!** 🎉
