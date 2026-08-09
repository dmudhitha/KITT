"""
System Control Plugin for VANGUARD AI Assistant.
Provides commands for OS volume control, desktop screenshots, and screen locking.
"""
import os
import time
import subprocess
import logging
from typing import List, Dict, Any
from commands import BasePlugin
from utils import play_sound_async

logger = logging.getLogger("vanguard.commands.system_control")


class SystemControlPlugin(BasePlugin):
    """Executes local OS system control commands."""

    @property
    def name(self) -> str:
        return "SystemControl"

    @property
    def description(self) -> str:
        return "Executes local OS system control directives (volume, screenshots, screen locking)."

    @property
    def commands(self) -> List[str]:
        return [
            "volume", "mute", "unmute",
            "screenshot", "capture screen",
            "lock screen", "lock pc"
        ]

    def execute(self, trigger: str, args: str, context: Dict[str, Any]) -> str:
        full_command = f"{trigger} {args}".lower().strip()

        # 1. Screenshot Handler
        if "screenshot" in full_command or "capture screen" in full_command:
            return self._take_screenshot()

        # 2. Lock Screen Handler
        if "lock screen" in full_command or "lock pc" in full_command:
            return self._lock_screen()

        # 3. Volume Control Handler
        if "volume" in full_command or "mute" in full_command or "unmute" in full_command:
            return self._control_volume(full_command)

        return "System Control command unrecognized."

    def _take_screenshot(self) -> str:
        """Captures a screenshot of the primary desktop display."""
        try:
            screenshots_dir = "assets/screenshots"
            os.makedirs(screenshots_dir, exist_ok=True)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = os.path.join(screenshots_dir, filename)

            # Try PIL ImageGrab
            try:
                from PIL import ImageGrab
                img = ImageGrab.grab()
                img.save(filepath)
            except Exception:
                # Fallback to scrot / gnome-screenshot
                subprocess.run(["scrot", filepath], check=True)

            play_sound_async("assets/sounds/plugin.wav")
            logger.info(f"Desktop screenshot saved to: {filepath}")
            return f"DESKTOP SCREENSHOT CAPTURED. Saved to: {filepath}"
        except Exception as e:
            play_sound_async("assets/sounds/error.wav")
            logger.error(f"Screenshot capture failed: {e}")
            return f"SYSTEM CONTROL ERROR: Could not capture screenshot ({e})."

    def _lock_screen(self) -> str:
        """Locks the local OS user session."""
        try:
            play_sound_async("assets/sounds/plugin.wav")
            # Try standard lock commands
            lock_cmds = [
                ["loginctl", "lock-session"],
                ["xdg-screensaver", "lock"],
                ["gnome-screensaver-command", "-l"]
            ]
            for c in lock_cmds:
                try:
                    subprocess.run(c, check=True)
                    logger.info(f"Screen locked via command: {' '.join(c)}")
                    return "SYSTEM SECURITY ENGAGED: Screen session locked."
                except Exception:
                    continue

            return "SYSTEM SECURITY NOTICE: Lock command attempted."
        except Exception as e:
            logger.error(f"Lock screen failed: {e}")
            return f"SYSTEM CONTROL ERROR: Lock command failed ({e})."

    def _control_volume(self, cmd_lower: str) -> str:
        """Adjusts system audio output volume."""
        try:
            play_sound_async("assets/sounds/plugin.wav")
            if "mute" in cmd_lower and "unmute" not in cmd_lower:
                subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "1"], check=False)
                return "AUDIO SYSTEM: Volume muted."
            elif "unmute" in cmd_lower:
                subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "0"], check=False)
                return "AUDIO SYSTEM: Volume unmuted."

            # Extract percentage volume number if present
            words = cmd_lower.split()
            vol_pct = None
            for w in words:
                clean_w = w.replace("%", "")
                if clean_w.isdigit():
                    vol_pct = int(clean_w)
                    break

            if vol_pct is not None:
                vol_pct = max(0, min(100, vol_pct))
                subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{vol_pct}%"], check=False)
                return f"AUDIO SYSTEM: Master volume adjusted to {vol_pct}%."

            if "up" in cmd_lower:
                subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "+10%"], check=False)
                return "AUDIO SYSTEM: Volume increased by 10%."
            elif "down" in cmd_lower:
                subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "-10%"], check=False)
                return "AUDIO SYSTEM: Volume decreased by 10%."

            return "AUDIO SYSTEM: Volume control directive processed."
        except Exception as e:
            return f"AUDIO SYSTEM ERROR: {e}"
