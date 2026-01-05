import json
import uuid as uuid_lib
import subprocess
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class XrayManager:
    def __init__(self, config_path: str = "/usr/local/etc/xray/config.json"):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self) -> dict:
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
        except:
            pass
        return self.get_default_config()
    
    def save_config(self):
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            self.restart_xray()
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def restart_xray(self):
        try:
            subprocess.run(['systemctl', 'restart', 'xray'], check=False)
        except:
            pass
    
    def get_default_config(self) -> dict:
        return {
            "log": {
                "loglevel": "warning"
            },
            "inbounds": [
                {
                    "port": 443,
                    "protocol": "vless",
                    "tag": "vless-ws-tls",
                    "settings": {
                        "clients": [],
                        "decryption": "none"
                    },
                    "streamSettings": {
                        "network": "ws",
                        "security": "tls",
                        "tlsSettings": {
                            "certificates": [
                                {
                                    "certificateFile": "/etc/xray/cert.crt",
                                    "keyFile": "/etc/xray/cert.key"
                                }
                            ]
                        },
                        "wsSettings": {
                            "path": "/vless-ws"
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
                        "wsSettings": {
                            "path": "/vless"
                        }
                    }
                },
                {
                    "port": 8443,
                    "protocol": "vmess",
                    "tag": "vmess-ws-tls",
                    "settings": {
                        "clients": []
                    },
                    "streamSettings": {
                        "network": "ws",
                        "security": "tls",
                        "tlsSettings": {
                            "certificates": [
                                {
                                    "certificateFile": "/etc/xray/cert.crt",
                                    "keyFile": "/etc/xray/cert.key"
                                }
                            ]
                        },
                        "wsSettings": {
                            "path": "/vmess-ws"
                        }
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
                        "wsSettings": {
                            "path": "/vmess"
                        }
                    }
                },
                {
                    "port": 445,
                    "protocol": "trojan",
                    "tag": "trojan-ws-tls",
                    "settings": {
                        "clients": []
                    },
                    "streamSettings": {
                        "network": "ws",
                        "security": "tls",
                        "tlsSettings": {
                            "certificates": [
                                {
                                    "certificateFile": "/etc/xray/cert.crt",
                                    "keyFile": "/etc/xray/cert.key"
                                }
                            ]
                        },
                        "wsSettings": {
                            "path": "/trojan-ws"
                        }
                    }
                },
                {
                    "port": 8081,
                    "protocol": "trojan",
                    "tag": "trojan-tcp",
                    "settings": {
                        "clients": []
                    },
                    "streamSettings": {
                        "network": "tcp",
                        "security": "tls",
                        "tlsSettings": {
                            "certificates": [
                                {
                                    "certificateFile": "/etc/xray/cert.crt",
                                    "keyFile": "/etc/xray/cert.key"
                                }
                            ]
                        }
                    }
                }
            ],
            "outbounds": [
                {
                    "protocol": "freedom",
                    "tag": "direct"
                },
                {
                    "protocol": "blackhole",
                    "tag": "block"
                }
            ]
        }
    
    def add_client(self, protocol: str, email: str, uuid: str = None, connection_type: str = "ws") -> Dict:
        if uuid is None:
            uuid = str(uuid_lib.uuid4())
        
        inbound_tag = f"{protocol}-{connection_type}"
        if "tls" in connection_type or "ssl" in connection_type:
            inbound_tag += "-tls"
        
        for inbound in self.config.get('inbounds', []):
            if inbound.get('tag') == inbound_tag or inbound.get('protocol') == protocol:
                client = {
                    "email": email
                }
                
                if protocol == "vmess":
                    client["id"] = uuid
                    client["alterId"] = 0
                elif protocol == "vless":
                    client["id"] = uuid
                    client["flow"] = ""
                elif protocol == "trojan":
                    client["password"] = uuid
                
                if 'clients' not in inbound['settings']:
                    inbound['settings']['clients'] = []
                
                inbound['settings']['clients'].append(client)
                self.save_config()
                
                return {
                    "uuid": uuid,
                    "email": email,
                    "protocol": protocol,
                    "connection_type": connection_type
                }
        
        return None
    
    def remove_client(self, email: str) -> bool:
        for inbound in self.config.get('inbounds', []):
            clients = inbound.get('settings', {}).get('clients', [])
            for i, client in enumerate(clients):
                if client.get('email') == email:
                    clients.pop(i)
                    self.save_config()
                    return True
        return False
    
    def get_client_info(self, email: str) -> Optional[Dict]:
        for inbound in self.config.get('inbounds', []):
            clients = inbound.get('settings', {}).get('clients', [])
            for client in clients:
                if client.get('email') == email:
                    return {
                        "protocol": inbound.get('protocol'),
                        "tag": inbound.get('tag'),
                        "client": client
                    }
        return None
    
    def generate_link(self, protocol: str, uuid: str, email: str, 
                     connection_type: str, domain: str, port: int = None) -> str:
        import base64
        
        if protocol == "vmess":
            if port is None:
                port = 8443 if "tls" in connection_type or "ssl" in connection_type else 8080
            
            vmess_config = {
                "v": "2",
                "ps": email,
                "add": domain,
                "port": str(port),
                "id": uuid,
                "aid": "0",
                "net": connection_type.replace("-tls", "").replace("-ssl", ""),
                "type": "none",
                "host": domain,
                "path": "/vmess-ws" if "tls" in connection_type else "/vmess",
                "tls": "tls" if "tls" in connection_type or "ssl" in connection_type else ""
            }
            
            json_str = json.dumps(vmess_config)
            encoded = base64.b64encode(json_str.encode()).decode()
            return f"vmess://{encoded}"
        
        elif protocol == "vless":
            if port is None:
                port = 443 if "tls" in connection_type or "ssl" in connection_type else 80
            
            path = "/vless-ws" if "tls" in connection_type else "/vless"
            security = "tls" if "tls" in connection_type or "ssl" in connection_type else "none"
            net_type = connection_type.replace("-tls", "").replace("-ssl", "")
            
            link = f"vless://{uuid}@{domain}:{port}?"
            link += f"type={net_type}&security={security}&path={path}&host={domain}#{email}"
            return link
        
        elif protocol == "trojan":
            if port is None:
                if "tcp" in connection_type:
                    port = 8081
                else:
                    port = 445
            
            path = "/trojan-ws" if "ws" in connection_type else ""
            security = "tls"
            net_type = "tcp" if "tcp" in connection_type else "ws"
            
            link = f"trojan://{uuid}@{domain}:{port}?"
            if path:
                link += f"type={net_type}&security={security}&path={path}&host={domain}#{email}"
            else:
                link += f"security={security}&type={net_type}#{email}"
            return link
        
        return ""
