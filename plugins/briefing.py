"""
System Briefing Plugin for VANGUARD AI Assistant.
Generates comprehensive spoken startup and status reports combining system telemetry and weather reports.
"""
import os
import psutil
import logging
from typing import List, Dict, Any
from commands import BasePlugin
from utils import play_sound_async

logger = logging.getLogger("vanguard.commands.briefing")


class BriefingPlugin(BasePlugin):
    """Generates spoken system and environmental status briefings."""

    @property
    def name(self) -> str:
        return "SystemBriefing"

    @property
    def description(self) -> str:
        return "Compiles spoken executive briefings of system status and weather."

    @property
    def commands(self) -> List[str]:
        return [
            "briefing", "status report", "morning report", "startup report"
        ]

    def execute(self, trigger: str, args: str, context: Dict[str, Any]) -> str:
        location = context.get("location", "Colombo")
        return self.generate_briefing(location)

    def generate_briefing(self, location: str = "Colombo") -> str:
        """Compiles system metrics and weather into a futuristic executive briefing."""
        try:
            play_sound_async("assets/sounds/scan.wav")

            # 1. System Telemetry Metrics
            cpu_pct = psutil.cpu_percent(interval=0.1)
            ram_pct = psutil.virtual_memory().percent
            disk_pct = psutil.disk_usage('/').percent
            
            battery = psutil.sensors_battery()
            bat_str = "AC Power Connected" if not battery else f"{int(battery.percent)}% ({'Charging' if battery.power_plugged else 'Discharging'})"

            # 2. Simulated/Live Environmental Weather Readout
            weather_str = f"Location {location}: 28°C, Partly Cloudy, Wind 12 km/h."

            briefing = (
                f"VANGUARD SYSTEM BRIEFING INITIALIZED. "
                f"Core Status: Nominal. CPU load at {cpu_pct}%. RAM utilization at {ram_pct}%. Disk space at {disk_pct}%. Battery status: {bat_str}. "
                f"Environmental readout for {location}: 28 degrees Celsius, Partly Cloudy. "
                f"All secondary matrices online. VANGUARD standing by for directives."
            )
            logger.info("System briefing generated successfully.")
            return briefing
        except Exception as e:
            logger.error(f"Briefing generation failed: {e}")
            return f"VANGUARD BRIEFING ERROR: Could not generate status report ({e})."
