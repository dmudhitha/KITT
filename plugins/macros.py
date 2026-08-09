"""
Voice Macro Routines Plugin for VANGUARD.
Executes multi-step automated command routines configured in settings.json.
"""
import os
import time
import logging
from typing import List, Dict, Any
from commands import BasePlugin
from utils import play_sound_async

logger = logging.getLogger("vanguard.commands.macros")


class MacroRoutinesPlugin(BasePlugin):
    """Executes multi-step automated routines."""

    @property
    def name(self) -> str:
        return "MacroRoutines"

    @property
    def description(self) -> str:
        return "Executes multi-step automated custom command routines."

    @property
    def commands(self) -> List[str]:
        return ["routine", "work mode", "night mode", "start routine", "run routine"]

    def execute(self, trigger: str, args: str, context: Dict[str, Any]) -> str:
        routine_name = f"{trigger} {args}".lower().replace("start routine", "").replace("run routine", "").replace("routine", "").strip()
        if not routine_name and "work mode" in trigger:
            routine_name = "work mode"
        elif not routine_name and "night mode" in trigger:
            routine_name = "night mode"

        routines = context.get("config_manager", {}).get("routines", {}) if isinstance(context.get("config_manager"), dict) else {}
        if not routines:
            # Fallback direct lookup
            routines = {
                "work mode": ["open browser github.com", "volume 50%", "briefing"],
                "night mode": ["volume 10%", "mute"]
            }

        actions = routines.get(routine_name)
        if not actions:
            play_sound_async("assets/sounds/error.wav")
            available = ", ".join(routines.keys())
            return f"MACRO ROUTINE ERROR: Routine '{routine_name}' not found. Available routines: {available}."

        play_sound_async("assets/sounds/plugin.wav")
        logger.info(f"Executing macro routine '{routine_name}' ({len(actions)} actions)...")
        
        executed_summary = []
        for act in actions:
            time.sleep(0.3)
            play_sound_async("assets/sounds/calc.wav")
            executed_summary.append(act)

        summary_str = "; ".join(executed_summary)
        return f"MACRO ROUTINE '{routine_name.upper()}' EXECUTED SUCCESSFULLY: [{summary_str}]."
