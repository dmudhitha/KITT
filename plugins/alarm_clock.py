"""
Alarm Clock and Task Scheduler Plugin for VANGUARD AI Assistant.
Parses clock time expressions and schedules background vocal alarm alerts.
"""
import re
import os
import time
import datetime
import threading
import logging
from typing import List, Dict, Any
from commands import BasePlugin
from utils import play_sound_async

logger = logging.getLogger("vanguard.commands.alarm_clock")


class AlarmClockPlugin(BasePlugin):
    """Manages clock-time alarms and task scheduling."""

    @property
    def name(self) -> str:
        return "AlarmClock"

    @property
    def description(self) -> str:
        return "Schedules background alarms for specific clock times."

    @property
    def commands(self) -> List[str]:
        return ["set alarm", "alarm for", "daily alarm", "alarm clock"]

    def execute(self, trigger: str, args: str, context: Dict[str, Any]) -> str:
        full_text = f"{trigger} {args}".lower().strip()

        # Parse target hour and minute
        target_time, task = self._parse_alarm_time(full_text)
        if not target_time:
            play_sound_async("assets/sounds/error.wav")
            return "ALARM CLOCK ERROR: Specify a valid clock time (e.g., 'set alarm for 5:00 PM to submit report' or 'set alarm for 17:30')."

        now = datetime.datetime.now()
        target_dt = datetime.datetime.combine(now.date(), target_time)
        if target_dt <= now:
            # Schedule for tomorrow if time has passed today
            target_dt += datetime.timedelta(days=1)

        seconds_until = (target_dt - now).total_seconds()
        ui_app = context.get("ui_app") if isinstance(context, dict) else None

        def alarm_worker():
            play_sound_async("assets/sounds/wake.wav")
            alarm_msg = f"VANGUARD ALARM CLOCK: Target time {target_dt.strftime('%H:%M')} reached! Task directive: {task}."
            logger.info(f"Alarm clock triggered: {alarm_msg}")
            
            try:
                if ui_app and hasattr(ui_app, "speak"):
                    ui_app.console_print(alarm_msg, prefix="[ALARM CLOCK] >> ")
                    ui_app.speak(alarm_msg)
            except Exception as e:
                logger.error(f"Alarm delivery failed: {e}")

        t = threading.Timer(seconds_until, alarm_worker)
        t.daemon = True
        t.start()

        play_sound_async("assets/sounds/plugin.wav")
        hrs = int(seconds_until // 3600)
        mins = int((seconds_until % 3600) // 60)
        time_str = f"{hrs}h {mins}m" if hrs > 0 else f"{mins} minute(s)"
        formatted_target = target_dt.strftime("%I:%M %p (%Y-%m-%d)")
        return f"ALARM CLOCK ENGAGED: Alarm set for {formatted_target} (in {time_str}) -> '{task}'."

    def _parse_alarm_time(self, text: str):
        """Parses time string like 5:00 PM, 17:30, 8:15 AM."""
        time_match = re.search(r'(\d{1,2}):(\d{2})\s*(am|pm)?', text)
        if not time_match:
            time_match = re.search(r'(\d{1,2})\s*(am|pm)', text)
            if time_match:
                hr = int(time_match.group(1))
                mn = 0
                ampm = time_match.group(2)
            else:
                return None, "check task directive"
        else:
            hr = int(time_match.group(1))
            mn = int(time_match.group(2))
            ampm = time_match.group(3)

        if ampm:
            ampm = ampm.lower()
            if ampm == "pm" and hr < 12:
                hr += 12
            elif ampm == "am" and hr == 12:
                hr = 0

        target_t = datetime.time(hour=max(0, min(23, hr)), minute=max(0, min(59, mn)))

        # Extract task
        task_match = re.search(r'to\s+(.+)', text)
        task = task_match.group(1).strip() if task_match else "execute target directive"
        return target_t, task
