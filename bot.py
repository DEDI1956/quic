import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional
import qrcode
from io import BytesIO

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from database import init_db, get_db, User, VPNAccount, Transaction
from xray_manager import XrayManager
from keyboards import (
    main_menu_keyboard,
    buy_account_keyboard,
    duration_keyboard,
    confirm_purchase_keyboard,
    my_accounts_keyboard,
    account_detail_keyboard,
    admin_menu_keyboard,
    payment_method_keyboard,
    trial_keyboard,
    back_keyboard
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "telegram": {
        "bot_token": "",
        "admin_ids": []
    },
    "xray": {
        "api_port": 10085,
        "config_path": "/usr/local/etc/xray/config.json"
    },
    "server": {
        "domain": "",
        "ip": ""
    },
    "pricing": {
        "vmess_ws": 10000,
        "vmess_ws_tls": 12000,
        "vless_ws": 12000,
        "vless_ws_tls": 15000,
        "vless_tcp_tls": 18000,
        "trojan_ws": 15000,
        "trojan_ws_tls": 18000,
        "trojan_tcp_tls": 20000
    },
    "trial": {
        "enabled": True,
        "duration_hours": 1
    }
}

CONFIG_PATH = os.getenv("BOT_CONFIG_PATH", "config.json")
try:
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    logger.warning(f"Config file '{CONFIG_PATH}' not found. Using default config and environment variables.")
    config = DEFAULT_CONFIG
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON in '{CONFIG_PATH}': {e}. Using default config.")
    config = DEFAULT_CONFIG

BOT_TOKEN = os.getenv('BOT_TOKEN') or config.get('telegram', {}).get('bot_token', '')
ADMIN_IDS = (
    [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]
    if os.getenv('ADMIN_IDS')
    else config.get('telegram', {}).get('admin_ids', [])
)
SERVER_DOMAIN = os.getenv('SERVER_DOMAIN') or config.get('server', {}).get('domain', '')
SERVER_IP = os.getenv('SERVER_IP') or config.get('server', {}).get('ip', '')
SERVER_HOST = SERVER_DOMAIN or SERVER_IP

XRAY_CONFIG_PATH = os.getenv('XRAY_CONFIG_PATH') or config.get('xray', {}).get('config_path')
XRAY_API_PORT = int(os.getenv('XRAY_API_PORT') or config.get('xray', {}).get('api_port', 10085))

XRAY_INIT_ERROR = None

try:
    xray = XrayManager(config_path=XRAY_CONFIG_PATH or None, api_port=XRAY_API_PORT)
    logger.info(f"XrayManager initialized: config_path={xray.config_path}, api_port={xray.api_port}")
except Exception as e:
    XRAY_INIT_ERROR = str(e)
    logger.critical(f"FATAL: Failed to initialize XrayManager: {e}")
    xray = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db = get_db()
    
    db_user = db.query(User).filter(User.telegram_id == user.id).first()
    if not db_user:
        db_user = User(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            is_admin=user.id in ADMIN_IDS
        )
        db.add(db_user)
        db.commit()
    
    is_admin = user.id in ADMIN_IDS
    
    welcome_text = f"""
🎉 Selamat datang di VPN Store Bot! 🎉

Halo {user.first_name}! 👋

Bot ini menyediakan layanan VPN premium dengan berbagai protokol:
• VMess (WebSocket, TCP, SSL/TLS)
• VLess (WebSocket, TCP, SSL/TLS)
• Trojan (WebSocket, TCP, SSL/TLS)

✨ Fitur Unggulan:
✅ Koneksi Cepat & Stabil
✅ Unlimited Bandwidth
✅ Support UDP
✅ 24/7 Online
✅ Harga Terjangkau

💰 Saldo Anda: Rp {db_user.balance:,.0f}

Silakan pilih menu di bawah untuk memulai:
"""
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=main_menu_keyboard(is_admin)
    )
    
    db.close()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    
    if text == "🛒 Beli Akun":
        await show_buy_menu(update, context)
    elif text == "👤 Akun Saya":
        await show_my_accounts(update, context)
    elif text == "💰 Top Up Saldo":
        await show_topup_menu(update, context)
    elif text == "📊 Status Server":
        await show_server_status(update, context)
    elif text == "🎁 Trial Gratis":
        await show_trial_menu(update, context)
    elif text == "📞 Hubungi Admin":
        await contact_admin(update, context)
    elif text == "⚙️ Panel Admin" and user_id in ADMIN_IDS:
        await show_admin_panel(update, context)

async def show_buy_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
🛒 **PILIH PROTOKOL VPN**

Silakan pilih protokol yang Anda inginkan:

📱 **VMess**: Protocol yang stabil dan cepat
🚀 **VLess**: Protocol ringan dan efisien  
🔐 **Trojan**: Protocol dengan keamanan tinggi

💡 Tips:
• WS = WebSocket (bypass firewall)
• TCP = Koneksi lebih stabil
• TLS = Enkripsi tambahan untuk keamanan
"""
    
    if update.callback_query:
        await update.callback_query.message.edit_text(
            text,
            reply_markup=buy_account_keyboard(),
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=buy_account_keyboard(),
            parse_mode='Markdown'
        )

async def show_my_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db = get_db()
    
    accounts = db.query(VPNAccount).filter(
        VPNAccount.telegram_id == user_id,
        VPNAccount.is_active == True
    ).all()
    
    if not accounts:
        text = "📭 Anda belum memiliki akun VPN.\n\nSilakan beli akun terlebih dahulu!"
        keyboard = [[InlineKeyboardButton("🛒 Beli Akun", callback_data="buy_account")]]
        markup = InlineKeyboardMarkup(keyboard)
    else:
        text = f"👤 **AKUN VPN ANDA**\n\nTotal akun aktif: {len(accounts)}\n\nPilih akun untuk melihat detail:"
        markup = my_accounts_keyboard(accounts)
    
    if update.callback_query:
        await update.callback_query.message.edit_text(
            text,
            reply_markup=markup,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=markup,
            parse_mode='Markdown'
        )
    
    db.close()

async def show_topup_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
💰 **TOP UP SALDO**

Silakan pilih nominal top up:

Minimum: Rp 10.000
Maximum: Rp 1.000.000

Ketik nominal yang ingin Anda top up (contoh: 50000)
atau pilih nominal di bawah:
"""
    
    keyboard = [
        [
            InlineKeyboardButton("Rp 10.000", callback_data="topup_10000"),
            InlineKeyboardButton("Rp 25.000", callback_data="topup_25000")
        ],
        [
            InlineKeyboardButton("Rp 50.000", callback_data="topup_50000"),
            InlineKeyboardButton("Rp 100.000", callback_data="topup_100000")
        ],
        [
            InlineKeyboardButton("Rp 200.000", callback_data="topup_200000"),
            InlineKeyboardButton("Rp 500.000", callback_data="topup_500000")
        ],
        [InlineKeyboardButton("« Kembali", callback_data="back_to_main")]
    ]
    
    if update.callback_query:
        await update.callback_query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

async def show_server_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"""
📊 **STATUS SERVER**

🌐 Domain: `{SERVER_DOMAIN}`
🖥 IP: `{SERVER_IP}`
✅ Status: Online
⚡ Uptime: 99.9%
📡 Load: Normal

🔌 Port yang aktif:
• VMess WS: 8080
• VMess WS TLS: 8443
• VLess WS: 80
• VLess WS TLS: 443
• Trojan WS TLS: 445
• Trojan TCP TLS: 8081

🕐 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    if update.callback_query:
        await update.callback_query.message.edit_text(
            text,
            reply_markup=back_keyboard(),
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=back_keyboard(),
            parse_mode='Markdown'
        )

async def show_trial_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db = get_db()
    
    existing_trial = db.query(VPNAccount).filter(
        VPNAccount.telegram_id == user_id,
        VPNAccount.email.like('%trial%')
    ).first()
    
    if existing_trial:
        text = "⚠️ Anda sudah pernah menggunakan trial sebelumnya.\n\nSilakan beli akun premium untuk melanjutkan!"
        keyboard = [[InlineKeyboardButton("🛒 Beli Akun", callback_data="buy_account")]]
    else:
        text = """
🎁 **TRIAL GRATIS**

Dapatkan akun trial gratis selama 1 jam!
Cocok untuk mencoba kecepatan dan kualitas server kami.

⚠️ Ketentuan:
• Durasi: 1 jam
• 1x per user
• Bandwidth: 1GB

Pilih protokol:
"""
        keyboard = trial_keyboard().inline_keyboard
    
    if update.callback_query:
        await update.callback_query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    db.close()

async def contact_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
📞 **HUBUNGI ADMIN**

Untuk pertanyaan, keluhan, atau bantuan:

👤 Admin: @youradmin
📱 WhatsApp: +62xxx-xxxx-xxxx
📧 Email: admin@yourdomain.com

⏰ Jam Kerja: 08:00 - 22:00 WIB

Kami akan merespons dalam 1-24 jam.
"""
    
    if update.callback_query:
        await update.callback_query.message.edit_text(
            text,
            reply_markup=back_keyboard(),
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=back_keyboard(),
            parse_mode='Markdown'
        )

async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Anda tidak memiliki akses ke panel admin!")
        return
    
    db = get_db()
    total_users = db.query(User).count()
    total_accounts = db.query(VPNAccount).filter(VPNAccount.is_active == True).count()
    total_transactions = db.query(Transaction).count()
    
    text = f"""
⚙️ **PANEL ADMIN**

📊 Statistik:
👥 Total User: {total_users}
🔑 Total Akun Aktif: {total_accounts}
💰 Total Transaksi: {total_transactions}

Pilih menu admin:
"""
    
    if update.callback_query:
        await update.callback_query.message.edit_text(
            text,
            reply_markup=admin_menu_keyboard(),
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=admin_menu_keyboard(),
            parse_mode='Markdown'
        )
    
    db.close()

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    
    if data == "back_to_main":
        await query.message.delete()
        return
    
    elif data == "buy_account" or data == "back_to_buy":
        await show_buy_menu(update, context)
    
    elif data == "back_to_accounts":
        await show_my_accounts(update, context)
    
    elif data.startswith("buy_"):
        protocol_conn = data.replace("buy_", "")
        parts = protocol_conn.split("_")
        protocol = parts[0]
        conn_type = "_".join(parts[1:])
        
        pricing = config['pricing']
        price_key = f"{protocol}_{conn_type}"
        base_price = pricing.get(price_key, 10000)
        
        text = f"""
💳 **BELI AKUN {protocol.upper()} {conn_type.upper().replace('_', ' ')}**

Pilih durasi berlangganan:

📅 Harga:
• 7 Hari: Rp {base_price * 0.7:,.0f}
• 15 Hari: Rp {base_price * 1.5:,.0f}
• 30 Hari: Rp {base_price * 3:,.0f}
• 60 Hari: Rp {base_price * 5:,.0f}

Pilih durasi:
"""
        
        await query.message.edit_text(
            text,
            reply_markup=duration_keyboard(protocol, conn_type),
            parse_mode='Markdown'
        )
    
    elif data.startswith("duration_"):
        parts = data.replace("duration_", "").split("_")
        days = int(parts[-1])
        conn_type = "_".join(parts[1:-1])
        protocol = parts[0]
        
        pricing = config['pricing']
        price_key = f"{protocol}_{conn_type}"
        base_price = pricing.get(price_key, 10000)
        
        price_multiplier = {7: 0.7, 15: 1.5, 30: 3, 60: 5}
        total_price = int(base_price * price_multiplier[days])
        
        db = get_db()
        user = db.query(User).filter(User.telegram_id == user_id).first()
        
        text = f"""
📝 **KONFIRMASI PEMBELIAN**

Protokol: {protocol.upper()} {conn_type.upper().replace('_', ' ')}
Durasi: {days} hari
Harga: Rp {total_price:,.0f}

💰 Saldo Anda: Rp {user.balance:,.0f}
"""
        
        if user.balance >= total_price:
            text += "\n✅ Saldo mencukupi!\n\nKonfirmasi pembelian?"
            keyboard = confirm_purchase_keyboard(protocol, conn_type, days)
        else:
            needed = total_price - user.balance
            text += f"\n❌ Saldo tidak mencukupi!\nKekurangan: Rp {needed:,.0f}\n\nSilakan top up terlebih dahulu."
            keyboard = [
                [InlineKeyboardButton("💰 Top Up", callback_data="topup")],
                [InlineKeyboardButton("« Kembali", callback_data="back_to_buy")]
            ]
            keyboard = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        db.close()
    
    elif data.startswith("confirm_"):
        parts = data.replace("confirm_", "").split("_")
        days = int(parts[-1])
        conn_type = "_".join(parts[1:-1])
        protocol = parts[0]
        
        await process_purchase(update, context, protocol, conn_type, days)
    
    elif data.startswith("account_"):
        account_id = int(data.replace("account_", ""))
        await show_account_detail(update, context, account_id)
    
    elif data.startswith("get_link_"):
        account_id = int(data.replace("get_link_", ""))
        await send_account_link(update, context, account_id)
    
    elif data.startswith("get_qr_"):
        account_id = int(data.replace("get_qr_", ""))
        await send_account_qr(update, context, account_id)
    
    elif data.startswith("trial_"):
        protocol_conn = data.replace("trial_", "")
        await create_trial_account(update, context, protocol_conn)
    
    elif data.startswith("topup_"):
        amount = int(data.replace("topup_", ""))
        await process_topup(update, context, amount)
    
    elif data.startswith("admin_"):
        await handle_admin_callback(update, context, data)

async def process_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                          protocol: str, conn_type: str, days: int):
    query = update.callback_query
    user_id = update.effective_user.id
    
    db = get_db()
    user = db.query(User).filter(User.telegram_id == user_id).first()
    
    # Check if XrayManager is available
    if xray is None:
        logger.error("XrayManager not initialized - cannot process purchase")
        error_detail = XRAY_INIT_ERROR or "XrayManager tidak terinisialisasi"
        await query.message.edit_text(
            "❌ Pembelian gagal karena layanan VPN belum siap.\n\n"
            f"Detail: {error_detail}\n\n"
            "Saldo Anda tidak dikurangi. Hubungi admin untuk bantuan.",
            reply_markup=back_keyboard()
        )
        db.close()
        return
    
    pricing = config.get('pricing', {})
    price_key = f"{protocol}_{conn_type}"
    base_price = pricing.get(price_key, 10000)
    price_multiplier = {7: 0.7, 15: 1.5, 30: 3, 60: 5}
    total_price = int(base_price * price_multiplier[days])
    
    if user.balance < total_price:
        await query.message.edit_text(
            "❌ Saldo tidak mencukupi!",
            reply_markup=back_keyboard()
        )
        db.close()
        return
    
    import uuid as uuid_lib
    uuid = str(uuid_lib.uuid4())
    email = f"{protocol}_{user_id}_{datetime.now().timestamp()}"

    result, error = xray.add_client(protocol, email, uuid, conn_type)

    if result:
        expired_at = datetime.now() + timedelta(days=days)
        
        new_account = VPNAccount(
            user_id=user.id,
            telegram_id=user_id,
            protocol=protocol,
            uuid=uuid,
            email=email,
            expired_at=expired_at,
            connection_type=conn_type
        )
        
        user.balance -= total_price
        
        transaction = Transaction(
            telegram_id=user_id,
            amount=total_price,
            type='purchase',
            description=f"{protocol.upper()} {conn_type.upper()} {days} hari",
            status='completed'
        )
        
        db.add(new_account)
        db.add(transaction)
        db.commit()
        
        link = xray.generate_link(protocol, uuid, email, conn_type, SERVER_HOST)
        
        text = f"""
✅ **PEMBELIAN BERHASIL!**

Akun VPN Anda telah dibuat:

📱 Protokol: {protocol.upper()} {conn_type.upper().replace('_', ' ')}
🆔 Email: `{email}`
🔑 UUID: `{uuid}`
📅 Expired: {expired_at.strftime('%Y-%m-%d %H:%M:%S')}

🔗 Link: `{link}`

💰 Sisa Saldo: Rp {user.balance:,.0f}

Gunakan tombol di bawah untuk mendapatkan QR Code.
"""
        
        keyboard = [
            [InlineKeyboardButton("📱 QR Code", callback_data=f"get_qr_{new_account.id}")],
            [InlineKeyboardButton("👤 Akun Saya", callback_data="my_accounts")],
            [InlineKeyboardButton("« Menu Utama", callback_data="back_to_main")]
        ]
        
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    else:
        error_msg = error or "Terjadi kesalahan tidak diketahui"
        logger.error(f"Failed to create account for user {user_id}: {error_msg}")
        await query.message.edit_text(
            f"❌ Gagal membuat akun VPN.\n\nError: {error_msg}\n\nSilakan hubungi admin atau coba lagi nanti.",
            reply_markup=back_keyboard()
        )
    
    db.close()

async def show_account_detail(update: Update, context: ContextTypes.DEFAULT_TYPE, account_id: int):
    query = update.callback_query
    user_id = update.effective_user.id
    
    db = get_db()
    account = db.query(VPNAccount).filter(
        VPNAccount.id == account_id,
        VPNAccount.telegram_id == user_id
    ).first()
    
    if not account:
        await query.message.edit_text(
            "❌ Akun tidak ditemukan!",
            reply_markup=back_keyboard()
        )
        db.close()
        return
    
    now = datetime.now()
    remaining = account.expired_at - now
    days_remaining = remaining.days
    
    status = "✅ Aktif" if account.is_active and account.expired_at > now else "❌ Expired"
    
    text = f"""
📱 **DETAIL AKUN VPN**

Protokol: {account.protocol.upper()} {account.connection_type.upper().replace('_', ' ')}
Status: {status}
Email: `{account.email}`
UUID: `{account.uuid}`

📅 Dibuat: {account.created_at.strftime('%Y-%m-%d %H:%M')}
⏰ Expired: {account.expired_at.strftime('%Y-%m-%d %H:%M')}
⏳ Sisa Waktu: {days_remaining} hari

Gunakan tombol di bawah untuk mendapatkan link atau QR code.
"""
    
    await query.message.edit_text(
        text,
        reply_markup=account_detail_keyboard(account_id),
        parse_mode='Markdown'
    )
    
    db.close()

async def send_account_link(update: Update, context: ContextTypes.DEFAULT_TYPE, account_id: int):
    query = update.callback_query
    user_id = update.effective_user.id
    
    db = get_db()
    account = db.query(VPNAccount).filter(
        VPNAccount.id == account_id,
        VPNAccount.telegram_id == user_id
    ).first()
    
    if not account:
        await query.answer("❌ Akun tidak ditemukan!", show_alert=True)
        db.close()
        return
    
    if xray is None:
        await query.answer("❌ Tidak bisa generate link: XrayManager tidak terinisialisasi", show_alert=True)
        db.close()
        return
    
    link = xray.generate_link(
        account.protocol,
        account.uuid,
        account.email,
        account.connection_type,
        SERVER_HOST
    )
    
    text = f"""
🔗 **LINK KONFIGURASI**

Protokol: {account.protocol.upper()}

`{link}`

Salin link di atas dan import ke aplikasi VPN Anda (V2RayNG, V2RayN, Clash, dll).
"""
    
    await query.answer("Link telah dikirim!")
    await context.bot.send_message(
        chat_id=user_id,
        text=text,
        parse_mode='Markdown'
    )
    
    db.close()

async def send_account_qr(update: Update, context: ContextTypes.DEFAULT_TYPE, account_id: int):
    query = update.callback_query
    user_id = update.effective_user.id
    
    db = get_db()
    account = db.query(VPNAccount).filter(
        VPNAccount.id == account_id,
        VPNAccount.telegram_id == user_id
    ).first()
    
    if not account:
        await query.answer("❌ Akun tidak ditemukan!", show_alert=True)
        db.close()
        return
    
    if xray is None:
        await query.answer("❌ Tidak bisa generate QR: XrayManager tidak terinisialisasi", show_alert=True)
        db.close()
        return
    
    link = xray.generate_link(
        account.protocol,
        account.uuid,
        account.email,
        account.connection_type,
        SERVER_HOST
    )
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(link)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    bio = BytesIO()
    bio.name = f'qr_{account.email}.png'
    img.save(bio, 'PNG')
    bio.seek(0)
    
    caption = f"""
📱 **QR CODE AKUN VPN**

Protokol: {account.protocol.upper()} {account.connection_type.upper().replace('_', ' ')}
Email: {account.email}

Scan QR code ini dengan aplikasi VPN Anda.
"""
    
    await query.answer("QR Code sedang dikirim...")
    await context.bot.send_photo(
        chat_id=user_id,
        photo=bio,
        caption=caption,
        parse_mode='Markdown'
    )
    
    db.close()

async def create_trial_account(update: Update, context: ContextTypes.DEFAULT_TYPE, protocol_conn: str):
    query = update.callback_query
    user_id = update.effective_user.id

    db = get_db()

    # Check if XrayManager is initialized
    if xray is None:
        logger.error("XrayManager not initialized - cannot create trial account")
        error_detail = XRAY_INIT_ERROR or "XrayManager tidak terinisialisasi"
        await query.message.edit_text(
            "❌ Layanan VPN belum siap karena konfigurasi server bermasalah.\n\n"
            f"Detail: {error_detail}\n\n"
            "Hubungi admin untuk bantuan.",
            reply_markup=back_keyboard()
        )
        db.close()
        return

    existing_trial = db.query(VPNAccount).filter(
        VPNAccount.telegram_id == user_id,
        VPNAccount.email.like('%trial%')
    ).first()

    if existing_trial:
        await query.message.edit_text(
            "⚠️ Anda sudah pernah menggunakan trial!",
            reply_markup=back_keyboard()
        )
        db.close()
        return

    # Trial selalu dibuat di inbound yang paling umum dan non-TLS: vmess-ws
    # (menghindari kegagalan jika server tidak menyediakan TLS/domain)
    protocol = "vmess"
    conn_type = "ws"

    healthy, health_msg = xray.check_health()
    if not healthy:
        logger.error(f"Xray health check failed for trial creation: {health_msg}")
        await query.message.edit_text(
            "❌ Trial gagal karena server VPN belum siap.\n\n"
            f"Detail: {health_msg}\n\n"
            "Silakan coba lagi nanti atau hubungi admin.",
            reply_markup=back_keyboard()
        )
        db.close()
        return

    is_accessible, config_msg = xray.check_config_accessibility()
    if not is_accessible:
        logger.error(f"Config accessibility check failed for trial creation: {config_msg}")
        await query.message.edit_text(
            "❌ Trial gagal karena bot tidak bisa menulis config Xray.\n\n"
            f"Detail: {config_msg}\n\n"
            "Hubungi admin untuk memperbaiki permission/konfigurasi.",
            reply_markup=back_keyboard()
        )
        db.close()
        return

    import uuid as uuid_lib
    uuid = str(uuid_lib.uuid4())
    email = f"trial_{protocol}_{user_id}_{datetime.now().timestamp()}"

    logger.info(f"Creating trial account for user {user_id}: {protocol} {conn_type}")
    result, error = xray.add_client(protocol, email, uuid, conn_type)

    if result:
        expired_at = datetime.now() + timedelta(hours=1)
        
        user = db.query(User).filter(User.telegram_id == user_id).first()
        
        new_account = VPNAccount(
            user_id=user.id,
            telegram_id=user_id,
            protocol=protocol,
            uuid=uuid,
            email=email,
            expired_at=expired_at,
            connection_type=conn_type
        )
        
        db.add(new_account)
        db.commit()

        link = xray.generate_link(protocol, uuid, email, conn_type, SERVER_HOST)

        text = f"""
        🎁 **TRIAL AKUN BERHASIL DIBUAT!**

Protokol: {protocol.upper()} WS
Email: `{email}`
UUID: `{uuid}`
Durasi: 1 Jam
Expired: {expired_at.strftime('%Y-%m-%d %H:%M:%S')}

🔗 Link: `{link}`

Silakan gunakan tombol di bawah untuk QR code.
"""
        
        keyboard = [
            [InlineKeyboardButton("📱 QR Code", callback_data=f"get_qr_{new_account.id}")],
            [InlineKeyboardButton("🛒 Beli Akun Premium", callback_data="buy_account")],
            [InlineKeyboardButton("« Menu Utama", callback_data="back_to_main")]
        ]
        
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    else:
        error_msg = error or "Terjadi kesalahan tidak diketahui"
        logger.error(f"Failed to create trial account for user {user_id}: {error_msg}")

        # Provide user-friendly error messages
        if "not running" in error_msg.lower():
            user_error = "❌ Layanan VPN sedang bermasalah.\n\nAdmin telah diberitahu. Silakan coba lagi nanti."
        elif "permission" in error_msg.lower():
            user_error = "❌ Terjadi masalah konfigurasi.\n\nAdmin telah diberitahu. Silakan hubungi admin."
        elif "not found" in error_msg.lower():
            user_error = "❌ Konfigurasi VPN tidak valid.\n\nHubungi admin untuk bantuan."
        else:
            user_error = f"❌ Gagal membuat akun trial.\n\nError: {error_msg}\n\nSilakan coba lagi nanti atau hubungi admin."

        await query.message.edit_text(
            user_error,
            reply_markup=back_keyboard()
        )

    db.close()

async def process_topup(update: Update, context: ContextTypes.DEFAULT_TYPE, amount: int):
    query = update.callback_query
    user_id = update.effective_user.id
    
    text = f"""
💳 **PEMBAYARAN TOP UP**

Jumlah: Rp {amount:,.0f}

Silakan transfer ke salah satu rekening:

🏦 **Bank BCA**
No. Rek: 1234567890
A/N: Nama Anda

💰 **E-Wallet (Dana/Gopay/OVO)**
No: 08123456789
A/N: Nama Anda

🏪 **Pulsa**
No: 08123456789 (Telkomsel)

⚠️ **Penting:**
1. Transfer sesuai nominal: Rp {amount:,.0f}
2. Setelah transfer, kirim bukti ke @youradmin
3. Saldo akan ditambahkan max 1x24 jam

ID Transaksi: #{user_id}{int(datetime.now().timestamp())}
"""
    
    db = get_db()
    transaction = Transaction(
        telegram_id=user_id,
        amount=amount,
        type='topup',
        description=f"Top up Rp {amount:,.0f}",
        status='pending'
    )
    db.add(transaction)
    db.commit()
    db.close()
    
    await query.message.edit_text(
        text,
        reply_markup=back_keyboard(),
        parse_mode='Markdown'
    )

async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
    query = update.callback_query
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await query.answer("⛔ Akses ditolak!", show_alert=True)
        return
    
    db = get_db()
    
    if data == "admin_users":
        users = db.query(User).all()
        text = f"👥 **TOTAL USER: {len(users)}**\n\n"
        for u in users[:20]:
            text += f"• {u.first_name} (@{u.username or 'N/A'}) - Saldo: Rp {u.balance:,.0f}\n"
        
        await query.message.edit_text(
            text,
            reply_markup=back_keyboard(),
            parse_mode='Markdown'
        )
    
    elif data == "admin_stats":
        total_users = db.query(User).count()
        total_accounts = db.query(VPNAccount).filter(VPNAccount.is_active == True).count()
        total_revenue = db.query(Transaction).filter(Transaction.type == 'purchase', Transaction.status == 'completed').count()
        
        text = f"""
📊 **STATISTIK**

👥 Total User: {total_users}
🔑 Akun Aktif: {total_accounts}
💰 Total Transaksi: {total_revenue}

📅 Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        await query.message.edit_text(
            text,
            reply_markup=back_keyboard(),
            parse_mode='Markdown'
        )
    
    elif data == "admin_accounts":
        accounts = db.query(VPNAccount).filter(VPNAccount.is_active == True).all()
        text = f"🔑 **SEMUA AKUN AKTIF: {len(accounts)}**\n\n"
        for acc in accounts[:20]:
            text += f"• {acc.protocol.upper()} - {acc.email[:30]}...\n"
        
        await query.message.edit_text(
            text,
            reply_markup=back_keyboard(),
            parse_mode='Markdown'
        )
    
    db.close()

def main():
    init_db()
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    logger.info("Bot started...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
