"""
Smart Voice Timers and Reminders Plugin for VANGUARD AI Assistant.
Parses countdown durations and triggers background vocal alarms and SFX notifications upon expiry.
"""
import re
import os
import time
import threading
import logging
from typing import List, Dict, Any
from commands import BasePlugin
from utils import play_sound_async

logger = logging.getLogger("vanguard.commands.reminders")


class RemindersPlugin(BasePlugin):
    """Manages voice timers and countdown reminders."""

    @property
    def name(self) -> str:
        return "Reminders"

    @property
    def description(self) -> str:
        return "Sets background countdown timers and vocal reminder alarms."

    @property
    def commands(self) -> List[str]:
        return ["remind me", "set reminder", "set timer", "timer"]

    def execute(self, trigger: str, args: str, context: Dict[str, Any]) -> str:
        full_text = f"{trigger} {args}".lower().strip()
        
        # Extract duration
        duration_seconds = self._parse_duration(full_text)
        if duration_seconds <= 0:
            play_sound_async("assets/sounds/error.wav")
            return "TIMER ERROR: Could not parse duration (e.g., 'remind me in 5 minutes to check deployment')."

        # Extract reminder task content
        task = self._extract_task(full_text)

        # Schedule background timer
        ui_app = context.get("ui_app") if isinstance(context, dict) else None
        
        def alarm_worker():
            play_sound_async("assets/sounds/wake.wav")
            alarm_msg = f"VANGUARD REMINDER ALARM: Time to {task}!"
            logger.info(f"Reminder alarm triggered: {alarm_msg}")
            
            # Print and speak via UI app if available
            try:
                from voice import SpeechSynthesizer
                # Synthesize vocal alarm
                if ui_app and hasattr(ui_app, "speak"):
                    ui_app.console_print(alarm_msg, prefix="[REMINDER ALARM] >> ")
                    ui_app.speak(alarm_msg)
            except Exception as e:
                logger.error(f"Alarm delivery failed: {e}")

        t = threading.Timer(duration_seconds, alarm_worker)
        t.daemon = True
        t.start()

        play_sound_async("assets/sounds/plugin.wav")
        mins = duration_seconds // 60
        secs = duration_seconds % 60
        time_str = f"{mins} minute(s)" if mins > 0 else f"{secs} second(s)"
        return f"TIMER ENGAGED: Reminder set for {time_str} -> '{task}'."

    def _parse_duration(self, text: str) -> int:
        """Extracts duration in seconds from natural text."""
        total_sec = 0
        # Match '10 minutes', '5 min', '30 seconds', '1 hour'
        hours = re.search(r'(\d+)\s*(?:hour|hours|hr|hrs)', text)
        minutes = re.search(r'(\d+)\s*(?:minute|minutes|min|mins)', text)
        seconds = re.search(r'(\d+)\s*(?:second|seconds|sec|secs)', text)

        if hours:
            total_sec += int(hours.group(1)) * 3600
        if minutes:
            total_sec += int(minutes.group(1)) * 60
        if seconds:
            total_sec += int(seconds.group(1))

        if total_sec == 0:
            # Check standalone number (default to minutes if unspecified)
            num_match = re.search(r'in\s+(\d+)', text)
            if num_match:
                total_sec = int(num_match.group(1)) * 60

        return total_sec

    def _extract_task(self, text: str) -> str:
        """Extracts target reminder prompt."""
        task_match = re.search(r'to\s+(.+)', text)
        if task_match:
            return task_match.group(1).strip()
        return "check active directive"
