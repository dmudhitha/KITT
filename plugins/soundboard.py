"""
Manual SFX Soundboard Plugin for VANGUARD AI Assistant.
Triggers multi-frequency sci-fi audio sound effects on command.
"""
import os
import logging
from typing import List, Dict, Any
from commands import BasePlugin
from utils import play_sound_async

logger = logging.getLogger("vanguard.commands.soundboard")


class SoundboardPlugin(BasePlugin):
    """Triggers sci-fi soundboard audio effects on directive."""

    @property
    def name(self) -> str:
        return "SFXSoundboard"

    @property
    def description(self) -> str:
        return "Triggers sci-fi audio sound effects on demand."

    @property
    def commands(self) -> List[str]:
        return ["play sound", "play sfx", "play tone", "sound effect"]

    def execute(self, trigger: str, args: str, context: Dict[str, Any]) -> str:
        sound_name = f"{trigger} {args}".lower().strip()

        sound_map = {
            "boot": "assets/sounds/boot.wav",
            "shutdown": "assets/sounds/shutdown.wav",
            "wake": "assets/sounds/wake.wav",
            "plugin": "assets/sounds/plugin.wav",
            "calc": "assets/sounds/calc.wav",
            "error": "assets/sounds/error.wav",
            "scan": "assets/sounds/scan.wav"
        }

        matched = None
        for key, sfile in sound_map.items():
            if key in sound_name:
                matched = sfile
                break

        if not matched:
            matched = "assets/sounds/plugin.wav"

        play_sound_async(matched)
        logger.info(f"Triggered SFX audio tone: {matched}")
        return f"AUDIO SYSTEM: Triggered sci-fi SFX playback -> {os.path.basename(matched)}."
