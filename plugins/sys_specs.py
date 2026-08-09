"""
Detailed OS Hardware Specs and Uptime Plugin for VANGUARD AI Assistant.
Compiles hardware architecture specifications and calculates system boot uptime.
"""
import time
import platform
import datetime
import psutil
import logging
from typing import List, Dict, Any
from commands import BasePlugin
from utils import play_sound_async

logger = logging.getLogger("vanguard.commands.sys_specs")


class HardwareSpecsPlugin(BasePlugin):
    """Compiles OS platform specs and system boot uptime telemetry."""

    @property
    def name(self) -> str:
        return "HardwareSpecs"

    @property
    def description(self) -> str:
        return "Compiles OS platform architecture specifications and calculates system uptime."

    @property
    def commands(self) -> List[str]:
        return ["system specs", "hardware specs", "uptime", "os specs", "system info"]

    def execute(self, trigger: str, args: str, context: Dict[str, Any]) -> str:
        try:
            play_sound_async("assets/sounds/scan.wav")

            # 1. OS & Architecture specs
            os_name = platform.system()
            os_release = platform.release()
            arch = platform.machine()
            cpu_count = psutil.cpu_count(logical=True)
            total_ram_gb = round(psutil.virtual_memory().total / (1024 ** 3), 1)

            # 2. Uptime calculation
            boot_t = datetime.datetime.fromtimestamp(psutil.boot_time())
            uptime_sec = (datetime.datetime.now() - boot_t).total_seconds()
            days = int(uptime_sec // 86400)
            hours = int((uptime_sec % 86400) // 3600)
            minutes = int((uptime_sec % 3600) // 60)

            uptime_str = f"{days}d {hours}h {minutes}m" if days > 0 else f"{hours}h {minutes}m"

            play_sound_async("assets/sounds/plugin.wav")
            report = (
                f"SYSTEM HARDWARE TELEMETRY REPORT: "
                f"OS: {os_name} {os_release} ({arch}). "
                f"CPU Cores: {cpu_count} | Total RAM: {total_ram_gb} GB. "
                f"System Uptime: {uptime_str} (Booted {boot_t.strftime('%Y-%m-%d %H:%M')}). "
                f"Diagnostic Status: Nominal."
            )
            logger.info("Hardware specs report compiled successfully.")
            return report
        except Exception as e:
            play_sound_async("assets/sounds/error.wav")
            logger.error(f"Hardware specs compilation failed: {e}")
            return f"HARDWARE SPECS ERROR: Survey failed ({e})."
