import qrcode
from io import BytesIO
from datetime import datetime, timedelta
import json
import base64

def generate_qr_code(data: str) -> BytesIO:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    bio = BytesIO()
    bio.name = 'qrcode.png'
    img.save(bio, 'PNG')
    bio.seek(0)
    
    return bio

def format_bytes(bytes_value: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"

def format_duration(seconds: int) -> str:
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    
    parts = []
    if days > 0:
        parts.append(f"{days} hari")
    if hours > 0:
        parts.append(f"{hours} jam")
    if minutes > 0:
        parts.append(f"{minutes} menit")
    
    return ", ".join(parts) if parts else "0 menit"

def generate_random_email(protocol: str, user_id: int) -> str:
    timestamp = int(datetime.now().timestamp())
    return f"{protocol}_{user_id}_{timestamp}"

def calculate_expiry(days: int) -> datetime:
    return datetime.now() + timedelta(days=days)

def is_expired(expiry_date: datetime) -> bool:
    return datetime.now() > expiry_date

def get_remaining_time(expiry_date: datetime) -> dict:
    if is_expired(expiry_date):
        return {"expired": True, "days": 0, "hours": 0, "minutes": 0}
    
    remaining = expiry_date - datetime.now()
    days = remaining.days
    hours = remaining.seconds // 3600
    minutes = (remaining.seconds % 3600) // 60
    
    return {
        "expired": False,
        "days": days,
        "hours": hours,
        "minutes": minutes,
        "total_seconds": remaining.total_seconds()
    }

def format_price(amount: float) -> str:
    return f"Rp {amount:,.0f}"

def validate_domain(domain: str) -> bool:
    import re
    pattern = r'^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$'
    return bool(re.match(pattern, domain.lower()))

def validate_ip(ip: str) -> bool:
    import re
    pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    return bool(re.match(pattern, ip))

def encode_vmess(config: dict) -> str:
    json_str = json.dumps(config)
    encoded = base64.b64encode(json_str.encode()).decode()
    return f"vmess://{encoded}"

def decode_vmess(link: str) -> dict:
    if not link.startswith("vmess://"):
        return None
    
    encoded = link.replace("vmess://", "")
    try:
        decoded = base64.b64decode(encoded).decode()
        return json.loads(decoded)
    except:
        return None

class RateLimiter:
    def __init__(self):
        self.requests = {}
    
    def check_rate_limit(self, user_id: int, max_requests: int = 10, window: int = 60) -> bool:
        now = datetime.now().timestamp()
        
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if now - req_time < window
        ]
        
        if len(self.requests[user_id]) >= max_requests:
            return False
        
        self.requests[user_id].append(now)
        return True

def get_protocol_info(protocol: str) -> dict:
    protocols = {
        "vmess": {
            "name": "VMess",
            "description": "Protocol yang stabil dan cepat",
            "encryption": "AES-128-GCM",
            "speed": "⭐⭐⭐⭐",
            "security": "⭐⭐⭐⭐"
        },
        "vless": {
            "name": "VLess",
            "description": "Protocol ringan dan efisien",
            "encryption": "NONE (TLS only)",
            "speed": "⭐⭐⭐⭐⭐",
            "security": "⭐⭐⭐⭐"
        },
        "trojan": {
            "name": "Trojan",
            "description": "Protocol dengan keamanan tinggi",
            "encryption": "TLS 1.3",
            "speed": "⭐⭐⭐⭐",
            "security": "⭐⭐⭐⭐⭐"
        }
    }
    
    return protocols.get(protocol, {})

def get_connection_info(connection_type: str) -> dict:
    connections = {
        "ws": {
            "name": "WebSocket",
            "description": "Bypass firewall dengan mudah",
            "stability": "⭐⭐⭐",
            "speed": "⭐⭐⭐⭐"
        },
        "ws_tls": {
            "name": "WebSocket TLS",
            "description": "WebSocket dengan enkripsi TLS",
            "stability": "⭐⭐⭐⭐",
            "speed": "⭐⭐⭐⭐"
        },
        "tcp": {
            "name": "TCP",
            "description": "Koneksi langsung, sangat stabil",
            "stability": "⭐⭐⭐⭐⭐",
            "speed": "⭐⭐⭐⭐⭐"
        },
        "tcp_tls": {
            "name": "TCP TLS",
            "description": "TCP dengan enkripsi TLS",
            "stability": "⭐⭐⭐⭐⭐",
            "speed": "⭐⭐⭐⭐"
        },
        "grpc": {
            "name": "gRPC",
            "description": "Protocol modern, sangat cepat",
            "stability": "⭐⭐⭐⭐",
            "speed": "⭐⭐⭐⭐⭐"
        }
    }
    
    return connections.get(connection_type, {})
