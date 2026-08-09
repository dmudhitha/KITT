"""
LAN Network Radar and Port Scanner Plugin for VANGUARD AI Assistant.
Scans active network interfaces, local IP bindings, and common open service ports.
"""
import socket
import psutil
import logging
from typing import List, Dict, Any
from commands import BasePlugin
from utils import play_sound_async

logger = logging.getLogger("vanguard.commands.network_radar")


class NetworkRadarPlugin(BasePlugin):
    """Executes local network interface and port survey scans."""

    @property
    def name(self) -> str:
        return "NetworkRadar"

    @property
    def description(self) -> str:
        return "Scans active network interfaces, local IP bindings, and open ports."

    @property
    def commands(self) -> List[str]:
        return ["scan network", "scan lan", "port scan", "network radar", "network survey"]

    def execute(self, trigger: str, args: str, context: Dict[str, Any]) -> str:
        try:
            play_sound_async("assets/sounds/scan.wav")

            # 1. Detect active IP addresses and interfaces
            local_ip = "127.0.0.1"
            iface_name = "loopback"
            addrs = psutil.net_if_addrs()
            for iface, addr_list in addrs.items():
                for addr in addr_list:
                    if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                        local_ip = addr.address
                        iface_name = iface
                        break
                if local_ip != "127.0.0.1":
                    break

            # 2. Scan common local service ports
            target_ports = {
                22: "SSH",
                80: "HTTP",
                443: "HTTPS",
                3000: "React/Node",
                5000: "Flask/Python",
                8080: "Web Proxy",
                11434: "Ollama LLM"
            }

            open_ports = []
            for port, service in target_ports.items():
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.15)
                res = sock.connect_ex((local_ip if local_ip != "127.0.0.1" else "127.0.0.1", port))
                if res == 0:
                    open_ports.append(f"{port} ({service})")
                sock.close()

            ports_str = ", ".join(open_ports) if open_ports else "None detected"
            report = (
                f"NETWORK RADAR SURVEY COMPLETE: "
                f"Active Interface: {iface_name} | Local IP: {local_ip}. "
                f"Active Open Ports: [{ports_str}]. "
                f"Link status: Operational. All network matrices nominal."
            )
            logger.info(f"Network radar survey report generated: {local_ip}")
            return report
        except Exception as e:
            play_sound_async("assets/sounds/error.wav")
            logger.error(f"Network radar scan failed: {e}")
            return f"NETWORK RADAR ERROR: Survey failed ({e})."
