import json
import uuid as uuid_lib
import subprocess
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class XrayManager:
    def __init__(self, config_path: str = "/usr/local/etc/xray/config.json"):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self) -> dict:
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
        return self.get_default_config()

    def check_service_status(self) -> Tuple[bool, str]:
        """
        Check if Xray service is running properly.
        Returns (is_running, message)
        """
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', 'xray'],
                capture_output=True,
                text=True,
                timeout=5
            )
            status = result.stdout.strip()
            if status == 'active':
                return True, "Xray service is running"
            else:
                return False, f"Xray service status: {status}"
        except subprocess.TimeoutExpired:
            return False, "Timeout checking Xray service status"
        except FileNotFoundError:
            return False, "systemctl command not found"
        except Exception as e:
            return False, f"Error checking service: {str(e)}"

    def check_config_accessibility(self) -> Tuple[bool, str]:
        """
        Check if Xray config file exists and is writable.
        Returns (is_accessible, message)
        """
        try:
            if not os.path.exists(self.config_path):
                return False, f"Config file not found: {self.config_path}"

            config_dir = os.path.dirname(self.config_path)
            if not os.access(config_dir, os.W_OK):
                return False, f"No write permission for config directory: {config_dir}"

            if os.path.exists(self.config_path) and not os.access(self.config_path, os.W_OK):
                return False, f"No write permission for config file: {self.config_path}"

            return True, "Config file is accessible"
        except Exception as e:
            return False, f"Error checking config accessibility: {str(e)}"

    def validate_protocol(self, protocol: str) -> bool:
        """Validate if the protocol is supported."""
        supported_protocols = ['vmess', 'vless', 'trojan']
        return protocol.lower() in supported_protocols

    def validate_connection_type(self, connection_type: str) -> bool:
        """Validate if the connection type is supported."""
        supported_types = ['ws', 'ws-tls', 'tcp', 'tcp-tls', 'ws-tls', 'ws-ssl']
        return connection_type.lower().replace('_', '-') in supported_types
    
    def save_config(self) -> Tuple[bool, str]:
        """
        Save config and restart Xray service.
        Returns (success, message)
        """
        try:
            # Check if config file is writable before attempting to save
            accessible, msg = self.check_config_accessibility()
            if not accessible:
                return False, msg

            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)

            restart_success, restart_msg = self.restart_xray()
            if not restart_success:
                return False, f"Config saved but restart failed: {restart_msg}"

            return True, "Config saved and Xray restarted successfully"
        except PermissionError as e:
            logger.error(f"Permission error saving config: {e}")
            return False, f"Permission denied: {str(e)}"
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False, f"Error saving config: {str(e)}"

    def restart_xray(self) -> Tuple[bool, str]:
        """
        Restart Xray service and verify it's running.
        Returns (success, message)
        """
        try:
            result = subprocess.run(
                ['systemctl', 'restart', 'xray'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return False, f"Restart command failed: {result.stderr}"

            # Wait a moment and check if service is running
            import time
            time.sleep(2)

            is_running, status_msg = self.check_service_status()
            return is_running, status_msg

        except subprocess.TimeoutExpired:
            logger.error("Timeout restarting Xray service")
            return False, "Timeout restarting Xray service"
        except FileNotFoundError:
            logger.error("systemctl command not found")
            return False, "systemctl command not found"
        except Exception as e:
            logger.error(f"Error restarting Xray: {e}")
            return False, f"Error restarting Xray: {str(e)}"
    
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
    
    def add_client(self, protocol: str, email: str, uuid: str = None, connection_type: str = "ws") -> Tuple[Optional[Dict], Optional[str]]:
        """
        Add a new client to Xray configuration.
        Returns (success_dict, error_message)
        """
        # Validate protocol
        if not self.validate_protocol(protocol):
            return None, f"Unsupported protocol: {protocol}"

        # Validate connection type
        if not self.validate_connection_type(connection_type):
            return None, f"Unsupported connection type: {connection_type}"

        # Check if Xray service is running
        is_running, service_msg = self.check_service_status()
        if not is_running:
            return None, f"Xray service not running: {service_msg}"

        # Check config accessibility
        is_accessible, config_msg = self.check_config_accessibility()
        if not is_accessible:
            return None, f"Config file error: {config_msg}"

        if uuid is None:
            uuid = str(uuid_lib.uuid4())

        inbound_tag = f"{protocol}-{connection_type}"
        if "tls" in connection_type or "ssl" in connection_type:
            inbound_tag += "-tls"

        # Find the appropriate inbound
        inbound_found = False
        for inbound in self.config.get('inbounds', []):
            if inbound.get('tag') == inbound_tag:
                inbound_found = True
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

                # Check for duplicate email
                for existing_client in inbound['settings']['clients']:
                    if existing_client.get('email') == email:
                        return None, f"Client with email '{email}' already exists"

                inbound['settings']['clients'].append(client)

                # Save config and restart
                save_success, save_msg = self.save_config()
                if not save_success:
                    return None, f"Failed to save config: {save_msg}"

                return {
                    "uuid": uuid,
                    "email": email,
                    "protocol": protocol,
                    "connection_type": connection_type
                }

        if not inbound_found:
            return None, f"Inbound tag '{inbound_tag}' not found in Xray configuration"

        return None, "Failed to add client: Unknown error"
    
    def remove_client(self, email: str) -> bool:
        for inbound in self.config.get('inbounds', []):
            clients = inbound.get('settings', {}).get('clients', [])
            for i, client in enumerate(clients):
                if client.get('email') == email:
                    clients.pop(i)
                    save_success, _ = self.save_config()
                    return save_success
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
