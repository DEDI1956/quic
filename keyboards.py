from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard(is_admin=False):
    keyboard = [
        [KeyboardButton("🛒 Beli Akun"), KeyboardButton("👤 Akun Saya")],
        [KeyboardButton("💰 Top Up Saldo"), KeyboardButton("📊 Status Server")],
        [KeyboardButton("🎁 Trial Gratis"), KeyboardButton("📞 Hubungi Admin")]
    ]
    
    if is_admin:
        keyboard.append([KeyboardButton("⚙️ Panel Admin")])
    
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def buy_account_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("VMess WS", callback_data="buy_vmess_ws"),
            InlineKeyboardButton("VMess WS TLS", callback_data="buy_vmess_ws_tls")
        ],
        [
            InlineKeyboardButton("VLess WS", callback_data="buy_vless_ws"),
            InlineKeyboardButton("VLess WS TLS", callback_data="buy_vless_ws_tls")
        ],
        [
            InlineKeyboardButton("VLess TCP TLS", callback_data="buy_vless_tcp_tls")
        ],
        [
            InlineKeyboardButton("Trojan WS", callback_data="buy_trojan_ws"),
            InlineKeyboardButton("Trojan WS TLS", callback_data="buy_trojan_ws_tls")
        ],
        [
            InlineKeyboardButton("Trojan TCP TLS", callback_data="buy_trojan_tcp_tls")
        ],
        [InlineKeyboardButton("« Kembali", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def duration_keyboard(protocol, conn_type):
    keyboard = [
        [
            InlineKeyboardButton("7 Hari", callback_data=f"duration_{protocol}_{conn_type}_7"),
            InlineKeyboardButton("15 Hari", callback_data=f"duration_{protocol}_{conn_type}_15")
        ],
        [
            InlineKeyboardButton("30 Hari", callback_data=f"duration_{protocol}_{conn_type}_30"),
            InlineKeyboardButton("60 Hari", callback_data=f"duration_{protocol}_{conn_type}_60")
        ],
        [InlineKeyboardButton("« Kembali", callback_data="back_to_buy")]
    ]
    return InlineKeyboardMarkup(keyboard)

def confirm_purchase_keyboard(protocol, conn_type, days):
    keyboard = [
        [
            InlineKeyboardButton("✅ Konfirmasi", callback_data=f"confirm_{protocol}_{conn_type}_{days}"),
            InlineKeyboardButton("❌ Batal", callback_data="back_to_buy")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def my_accounts_keyboard(accounts):
    keyboard = []
    for acc in accounts:
        button_text = f"{acc.protocol.upper()} - {acc.email}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"account_{acc.id}")])
    
    keyboard.append([InlineKeyboardButton("« Kembali", callback_data="back_to_main")])
    return InlineKeyboardMarkup(keyboard)

def account_detail_keyboard(account_id):
    keyboard = [
        [
            InlineKeyboardButton("🔗 Dapatkan Link", callback_data=f"get_link_{account_id}"),
            InlineKeyboardButton("📱 QR Code", callback_data=f"get_qr_{account_id}")
        ],
        [
            InlineKeyboardButton("♻️ Renew", callback_data=f"renew_{account_id}"),
            InlineKeyboardButton("🗑 Hapus", callback_data=f"delete_{account_id}")
        ],
        [InlineKeyboardButton("« Kembali", callback_data="back_to_accounts")]
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("👥 Total User", callback_data="admin_users"),
            InlineKeyboardButton("📊 Statistik", callback_data="admin_stats")
        ],
        [
            InlineKeyboardButton("💰 Transaksi", callback_data="admin_transactions"),
            InlineKeyboardButton("🔑 Semua Akun", callback_data="admin_accounts")
        ],
        [
            InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
            InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings")
        ],
        [InlineKeyboardButton("« Kembali", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def payment_method_keyboard(amount):
    keyboard = [
        [InlineKeyboardButton("💳 Transfer Bank", callback_data=f"payment_bank_{amount}")],
        [InlineKeyboardButton("💰 E-Wallet", callback_data=f"payment_ewallet_{amount}")],
        [InlineKeyboardButton("🏪 Pulsa", callback_data=f"payment_pulsa_{amount}")],
        [InlineKeyboardButton("« Batal", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def trial_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("VMess Trial", callback_data="trial_vmess_ws"),
            InlineKeyboardButton("VLess Trial", callback_data="trial_vless_ws")
        ],
        [
            InlineKeyboardButton("Trojan Trial", callback_data="trial_trojan_ws")
        ],
        [InlineKeyboardButton("« Kembali", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_keyboard():
    keyboard = [[InlineKeyboardButton("« Kembali", callback_data="back_to_main")]]
    return InlineKeyboardMarkup(keyboard)
