"""
Diagnostics Module for VANGUARD Assistant.
Polls system telemetry including CPU, RAM, Disk, battery status, network, and temperatures.
"""
import socket
import logging
from typing import Dict, Any, Optional
import psutil

logger = logging.getLogger("vanguard.diagnostics")


class SystemDiagnostics:
    """Gathers real-time machine hardware and connectivity diagnostics."""

    def __init__(self):
        logger.info("VANGUARD Diagnostics Engine initialized.")

    def get_diagnostics_report(self) -> Dict[str, Any]:
        """Gathers a snapshot of system vitals."""
        return {
            "cpu_percent": self._get_cpu_percent(),
            "ram_percent": self._get_ram_percent(),
            "disk_percent": self._get_disk_percent(),
            "battery": self._get_battery_status(),
            "network_online": self._check_network_status(),
            "cpu_temp": self._get_cpu_temperature()
        }

    def _get_cpu_percent(self) -> float:
        """Returns CPU usage percentage."""
        try:
            # interval=None does a non-blocking poll based on last call
            return psutil.cpu_percent(interval=None)
        except Exception as e:
            logger.error(f"Error fetching CPU: {e}")
            return 0.0

    def _get_ram_percent(self) -> float:
        """Returns RAM usage percentage."""
        try:
            return psutil.virtual_memory().percent
        except Exception as e:
            logger.error(f"Error fetching RAM: {e}")
            return 0.0

    def _get_disk_percent(self) -> float:
        """Returns root disk space percentage."""
        try:
            return psutil.disk_usage("/").percent
        except Exception as e:
            logger.error(f"Error fetching Disk: {e}")
            return 0.0

    def _get_battery_status(self) -> Dict[str, Any]:
        """Returns battery charge level and charging status."""
        try:
            battery = psutil.sensors_battery()
            if battery is None:
                return {"present": False, "percent": 100, "power_plugged": True}
            return {
                "present": True,
                "percent": battery.percent,
                "power_plugged": battery.power_plugged
            }
        except Exception as e:
            logger.debug(f"Sensors battery query unsupported or failed: {e}")
            return {"present": False, "percent": 100, "power_plugged": True}

    def _check_network_status(self) -> bool:
        """Checks internet connectivity by attempting socket connection to DNS server."""
        try:
            # 8.8.8.8 is Google DNS. Timeout 0.5s prevents stalling the poll
            socket.setdefaulttimeout(0.5)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("8.8.8.8", 53))
            s.close()
            return True
        except (socket.error, OSError):
            return False

    def _get_cpu_temperature(self) -> Optional[float]:
        """Reads CPU core temperatures if supported by the OS and hardware."""
        try:
            temps = psutil.sensors_temperatures()
            if not temps:
                return None
            
            # Common sensor tags for CPU temps
            for name in ["coretemp", "cpu_thermal", "acpitz", "k10temp"]:
                if name in temps:
                    sensor_list = temps[name]
                    if sensor_list:
                        # Return current temp of first sensor core
                        return sensor_list[0].current
            
            # Fallback to first available sensor group
            first_key = list(temps.keys())[0]
            if temps[first_key]:
                return temps[first_key][0].current
        except Exception as e:
            logger.debug(f"Core temperature sensors unsupported: {e}")
        return None
