import base64
import json
import logging
import os
import shlex
import shutil
import socket
import subprocess
import tempfile
import uuid as uuid_lib
from datetime import datetime
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class XrayManager:
    DEFAULT_API_PORT = 10085
    COMMON_CONFIG_PATHS = (
        "/usr/local/etc/xray/config.json",
        "/etc/xray/config.json",
    )

    def __init__(self, config_path: Optional[str] = None, api_port: Optional[int] = None):
        self.api_port = api_port or int(os.getenv("XRAY_API_PORT", str(self.DEFAULT_API_PORT)))
        self.config_path = (
            config_path
            or os.getenv("XRAY_CONFIG_PATH")
            or self._detect_running_config_path()
            or self._pick_existing_common_path()
            or self.COMMON_CONFIG_PATHS[0]
        )

        self.config = self.load_config()

    def _run(self, cmd: List[str], timeout: int = 10) -> subprocess.CompletedProcess:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

    def _detect_running_config_path(self) -> Optional[str]:
        """Try to detect the config path used by the running xray service."""
        exec_start = None
        try:
            result = self._run(["systemctl", "show", "xray", "-p", "ExecStart", "--value"], timeout=5)
            if result.returncode == 0:
                exec_start = result.stdout.strip()
        except FileNotFoundError:
            exec_start = None
        except Exception:
            exec_start = None

        if exec_start:
            try:
                parts = shlex.split(exec_start)
                for idx, token in enumerate(parts):
                    if token in {"-config", "-c"} and idx + 1 < len(parts):
                        return parts[idx + 1]
                    if token.startswith("-config="):
                        return token.split("=", 1)[1]
            except Exception:
                pass

        # Fallback to process list
        for cmd in (["pgrep", "-a", "xray"], ["pgrep", "-af", "xray"]):
            try:
                result = self._run(cmd, timeout=3)
                if result.returncode != 0:
                    continue
                for line in result.stdout.splitlines():
                    try:
                        parts = shlex.split(line)
                    except Exception:
                        continue
                    for idx, token in enumerate(parts):
                        if token in {"-config", "-c"} and idx + 1 < len(parts):
                            return parts[idx + 1]
                        if token.startswith("-config="):
                            return token.split("=", 1)[1]
            except FileNotFoundError:
                break
            except Exception:
                continue

        return None

    def _pick_existing_common_path(self) -> Optional[str]:
        for p in self.COMMON_CONFIG_PATHS:
            if os.path.exists(p):
                return p
        return None

    def load_config(self) -> dict:
        """Load Xray config.

        WAJIB: Tidak ada fallback default config. Jika config missing/invalid -> fail keras.
        """
        if not os.path.exists(self.config_path):
            msg = f"CRITICAL: Xray config file not found: {self.config_path}"
            logger.error(msg)
            raise FileNotFoundError(msg)

        if not os.access(self.config_path, os.R_OK):
            msg = f"CRITICAL: No read permission for Xray config: {self.config_path}"
            logger.error(msg)
            raise PermissionError(msg)

        try:
            with open(self.config_path, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            msg = f"CRITICAL: Invalid JSON in Xray config {self.config_path}: {e}"
            logger.error(msg)
            raise ValueError(msg) from e

        if not isinstance(data, dict):
            raise ValueError("CRITICAL: Xray config must be a JSON object")

        if "inbounds" not in data or not isinstance(data["inbounds"], list):
            raise ValueError("CRITICAL: Xray config missing 'inbounds' array")

        logger.info("Loaded Xray config from %s", self.config_path)
        return data

    def reload_config(self) -> None:
        self.config = self.load_config()

    def check_config_accessibility(self) -> Tuple[bool, str]:
        try:
            if not os.path.exists(self.config_path):
                return False, f"Config file not found: {self.config_path}"

            config_dir = os.path.dirname(self.config_path)
            if not os.access(config_dir, os.W_OK):
                return False, f"No write permission for config directory: {config_dir}"

            if not os.access(self.config_path, os.W_OK):
                return False, f"No write permission for config file: {self.config_path}"

            return True, "Config file is accessible"
        except Exception as e:
            return False, f"Error checking config accessibility: {e}"

    def _check_process_running(self) -> Tuple[bool, str]:
        try:
            result = self._run(["pgrep", "-x", "xray"], timeout=3)
            if result.returncode == 0:
                return True, "Xray process is running"
            return False, "Xray process not found"
        except FileNotFoundError:
            return False, "pgrep not found"
        except Exception as e:
            return False, f"Error checking Xray process: {e}"

    def check_service_status(self) -> Tuple[bool, str]:
        """Validasi realistis: cukup cek service berjalan.

        - Utama: systemctl is-active xray
        - Fallback: pgrep xray (untuk environment tanpa systemd)
        """
        try:
            result = self._run(["systemctl", "is-active", "xray"], timeout=5)
            status = result.stdout.strip()
            if status == "active":
                return True, "Xray service is running"
            if status:
                return False, f"Xray service status: {status}"
            return False, "Unable to determine Xray service status"
        except FileNotFoundError:
            return self._check_process_running()
        except Exception as e:
            return False, f"Error checking service: {e}"

    def check_xray_api(self, api_port: Optional[int] = None) -> Tuple[bool, str]:
        port = int(api_port or self.api_port)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(("127.0.0.1", port))
            sock.close()
            if result == 0:
                return True, f"Xray API reachable on 127.0.0.1:{port}"
            return False, f"Xray API not reachable on 127.0.0.1:{port}"
        except Exception as e:
            return False, f"Error checking Xray API: {e}"

    def check_health(self) -> Tuple[bool, str]:
        """Validasi realistis sesuai ticket.

        Syarat OK:
        - Xray running
        - Xray API aktif
        """
        svc_ok, svc_msg = self.check_service_status()
        api_ok, api_msg = self.check_xray_api()

        if svc_ok and api_ok:
            return True, f"OK: {svc_msg}; {api_msg}"
        if not svc_ok and api_ok:
            return False, f"Xray API OK but service not OK: {svc_msg}"
        if svc_ok and not api_ok:
            return False, f"Xray service OK but API not OK: {api_msg}"
        return False, f"Xray unhealthy: {svc_msg}; {api_msg}"

    def validate_protocol(self, protocol: str) -> bool:
        return protocol.lower() in {"vmess", "vless", "trojan"}

    def validate_connection_type(self, connection_type: str) -> bool:
        if not connection_type:
            return False
        normalized = connection_type.lower().replace("_", "-")
        return normalized in {"ws", "ws-tls", "tcp", "tcp-tls", "ws-ssl"}

    def _normalize_connection_type(self, connection_type: str) -> str:
        return connection_type.lower().replace("_", "-")

    def _resolve_inbound_tag(self, protocol: str, connection_type: str) -> str:
        conn = self._normalize_connection_type(connection_type)
        is_tls = "tls" in conn or "ssl" in conn
        is_tcp = "tcp" in conn

        if is_tls and is_tcp:
            return f"{protocol}-tcp-tls"
        if is_tls:
            return f"{protocol}-ws-tls"
        if is_tcp:
            return f"{protocol}-tcp"
        return f"{protocol}-ws"

    def find_inbound_by_tag(self, tag: str) -> Optional[Dict]:
        for inbound in self.config.get("inbounds", []):
            if inbound.get("tag") == tag:
                return inbound
        return None

    def get_available_inbounds(self) -> List[str]:
        inbounds: List[str] = []
        for inbound in self.config.get("inbounds", []):
            tag = inbound.get("tag")
            if not tag or tag == "api":
                continue
            inbounds.append(f"{tag} ({inbound.get('protocol')}:{inbound.get('port')})")
        return inbounds

    def _atomic_write_json(self, path: str, data: Dict) -> None:
        directory = os.path.dirname(path)
        with tempfile.NamedTemporaryFile("w", dir=directory, delete=False) as tmp:
            json.dump(data, tmp, indent=2)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_path = tmp.name
        os.replace(tmp_path, path)

    def save_config(self) -> Tuple[bool, str]:
        accessible, msg = self.check_config_accessibility()
        if not accessible:
            return False, msg

        backup_path = f"{self.config_path}.backup.{int(datetime.now().timestamp())}"
        try:
            shutil.copy2(self.config_path, backup_path)
        except Exception as e:
            logger.warning("Could not backup config: %s", e)

        try:
            self._atomic_write_json(self.config_path, self.config)
        except Exception as e:
            return False, f"Failed to write config: {e}"

        ok, restart_msg = self.restart_xray()
        if not ok:
            return False, f"Config saved but failed to apply: {restart_msg}"

        try:
            self.reload_config()
        except Exception as e:
            return False, f"Config applied but reload failed: {e}"

        return True, "Config saved and applied"

    def restart_xray(self) -> Tuple[bool, str]:
        """Reload/restart xray.

        - Try reload first (if supported)
        - Fallback restart
        """
        try:
            reload = self._run(["systemctl", "reload", "xray"], timeout=10)
            if reload.returncode == 0:
                ok, msg = self.check_health()
                return ok, f"Reloaded: {msg}"

            restart = self._run(["systemctl", "restart", "xray"], timeout=15)
            if restart.returncode != 0:
                return False, f"Restart failed: {restart.stderr.strip()}"

            ok, msg = self.check_health()
            return ok, f"Restarted: {msg}"
        except FileNotFoundError:
            return False, "systemctl not found (cannot reload/restart automatically)"
        except subprocess.TimeoutExpired:
            return False, "Timeout while reloading/restarting xray"
        except Exception as e:
            return False, f"Error restarting xray: {e}"

    def _verify_client_applied(self, inbound_tag: str, email: str, uuid: str, protocol: str) -> Tuple[bool, str]:
        inbound = self.find_inbound_by_tag(inbound_tag)
        if not inbound:
            return False, f"Inbound '{inbound_tag}' not found after reload"

        clients = inbound.get("settings", {}).get("clients", [])
        for c in clients:
            if c.get("email") != email:
                continue
            if protocol in {"vmess", "vless"} and c.get("id") == uuid:
                return True, "Client verified"
            if protocol == "trojan" and c.get("password") == uuid:
                return True, "Client verified"
            return False, "Client email exists but UUID/password mismatch"

        return False, "Client not found after reload"

    def add_client(
        self,
        protocol: str,
        email: str,
        uuid: Optional[str] = None,
        connection_type: str = "ws",
    ) -> Tuple[Optional[Dict], Optional[str]]:
        if not self.validate_protocol(protocol):
            return None, f"Unsupported protocol: {protocol}"

        if not self.validate_connection_type(connection_type):
            return None, f"Unsupported connection type: {connection_type}"

        healthy, health_msg = self.check_health()
        if not healthy:
            return None, health_msg

        is_accessible, config_msg = self.check_config_accessibility()
        if not is_accessible:
            return None, config_msg

        if uuid is None:
            uuid = str(uuid_lib.uuid4())

        inbound_tag = self._resolve_inbound_tag(protocol, connection_type)
        inbound = self.find_inbound_by_tag(inbound_tag)
        if not inbound:
            available = ", ".join(self.get_available_inbounds())
            return None, f"Inbound '{inbound_tag}' not found. Available: {available}"

        inbound.setdefault("settings", {})
        inbound["settings"].setdefault("clients", [])

        for existing in inbound["settings"]["clients"]:
            if existing.get("email") == email:
                return None, f"Client with email '{email}' already exists"

        client: Dict[str, object] = {"email": email}
        if protocol == "vmess":
            client.update({"id": uuid, "alterId": 0})
        elif protocol == "vless":
            client.update({"id": uuid, "flow": ""})
        elif protocol == "trojan":
            client.update({"password": uuid})

        inbound["settings"]["clients"].append(client)

        saved, save_msg = self.save_config()
        if not saved:
            inbound["settings"]["clients"].pop()
            return None, save_msg

        ok, verify_msg = self._verify_client_applied(inbound_tag, email, uuid, protocol)
        if not ok:
            return None, f"Client added but verification failed: {verify_msg}"

        return {
            "uuid": uuid,
            "email": email,
            "protocol": protocol,
            "connection_type": connection_type,
            "inbound_tag": inbound_tag,
        }, None

    def remove_client(self, email: str) -> bool:
        removed = False
        for inbound in self.config.get("inbounds", []):
            clients = inbound.get("settings", {}).get("clients", [])
            for i, c in enumerate(list(clients)):
                if c.get("email") == email:
                    clients.pop(i)
                    removed = True
                    break

        if not removed:
            return False

        ok, _ = self.save_config()
        return ok

    def get_client_info(self, email: str) -> Optional[Dict]:
        for inbound in self.config.get("inbounds", []):
            clients = inbound.get("settings", {}).get("clients", [])
            for client in clients:
                if client.get("email") == email:
                    return {
                        "protocol": inbound.get("protocol"),
                        "tag": inbound.get("tag"),
                        "port": inbound.get("port"),
                        "client": client,
                    }
        return None

    def _guess_inbound_params(self, protocol: str, connection_type: str) -> Tuple[Optional[int], Optional[str]]:
        tag = self._resolve_inbound_tag(protocol, connection_type)
        inbound = self.find_inbound_by_tag(tag)
        if not inbound:
            return None, None

        port = inbound.get("port")
        ws_settings = (inbound.get("streamSettings") or {}).get("wsSettings") or {}
        path = ws_settings.get("path")
        return port, path

    def generate_link(
        self,
        protocol: str,
        uuid: str,
        email: str,
        connection_type: str,
        domain: str,
        port: int = None,
    ) -> str:
        if not domain:
            domain = "127.0.0.1"

        guessed_port, guessed_path = self._guess_inbound_params(protocol, connection_type)

        if protocol == "vmess":
            final_port = port or guessed_port or (8443 if "tls" in connection_type or "ssl" in connection_type else 8080)
            final_path = guessed_path or ("/vmess-ws" if "tls" in connection_type else "/vmess")

            vmess_config = {
                "v": "2",
                "ps": email,
                "add": domain,
                "port": str(final_port),
                "id": uuid,
                "aid": "0",
                "net": self._normalize_connection_type(connection_type).replace("-tls", "").replace("-ssl", ""),
                "type": "none",
                "host": domain,
                "path": final_path,
                "tls": "tls" if "tls" in connection_type or "ssl" in connection_type else "",
            }

            encoded = base64.b64encode(json.dumps(vmess_config).encode()).decode()
            return f"vmess://{encoded}"

        if protocol == "vless":
            final_port = port or guessed_port or (443 if "tls" in connection_type or "ssl" in connection_type else 80)
            final_path = guessed_path or ("/vless-ws" if "tls" in connection_type else "/vless")
            security = "tls" if "tls" in connection_type or "ssl" in connection_type else "none"
            net_type = self._normalize_connection_type(connection_type).replace("-tls", "").replace("-ssl", "")

            return (
                f"vless://{uuid}@{domain}:{final_port}?"
                f"type={net_type}&security={security}&path={final_path}&host={domain}#{email}"
            )

        if protocol == "trojan":
            final_port = port or guessed_port or (8081 if "tcp" in connection_type else 445)
            final_path = guessed_path or ("/trojan-ws" if "ws" in connection_type else "")
            net_type = "tcp" if "tcp" in connection_type else "ws"
            security = "tls" if "tls" in connection_type or "ssl" in connection_type else "none"

            if final_path:
                return (
                    f"trojan://{uuid}@{domain}:{final_port}?"
                    f"type={net_type}&security={security}&path={final_path}&host={domain}#{email}"
                )
            return f"trojan://{uuid}@{domain}:{final_port}?security={security}&type={net_type}#{email}"

        return ""
