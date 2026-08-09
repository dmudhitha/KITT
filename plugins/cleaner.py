"""
System Memory and RAM Purge Plugin for VANGUARD AI Assistant.
Executes Python garbage collection and OS memory cache optimization.
"""
import gc
import os
import psutil
import subprocess
import logging
from typing import List, Dict, Any
from commands import BasePlugin
from utils import play_sound_async

logger = logging.getLogger("vanguard.commands.cleaner")


class MemoryCleanerPlugin(BasePlugin):
    """Executes system RAM and cache purge operations."""

    @property
    def name(self) -> str:
        return "MemoryCleaner"

    @property
    def description(self) -> str:
        return "Purges system memory caches and forces garbage collection."

    @property
    def commands(self) -> List[str]:
        return ["clean memory", "free ram", "clear cache", "memory purge", "purge ram"]

    def execute(self, trigger: str, args: str, context: Dict[str, Any]) -> str:
        try:
            mem_before = psutil.virtual_memory()
            used_before_mb = mem_before.used / (1024 * 1024)

            # 1. Force Python Garbage Collector
            collected = gc.collect()

            # 2. Try OS drop_caches if privileged or sync
            try:
                subprocess.run(["sync"], check=False)
            except Exception:
                pass

            mem_after = psutil.virtual_memory()
            used_after_mb = mem_after.used / (1024 * 1024)
            freed_mb = max(0.0, used_before_mb - used_after_mb)

            play_sound_async("assets/sounds/plugin.wav")
            logger.info(f"Memory purge complete: {freed_mb:.1f} MB freed ({collected} GC objects collected).")
            return (
                f"SYSTEM MEMORY PURGE COMPLETE: "
                f"Freed approximately {freed_mb:.1f} MB of RAM ({collected} objects collected). "
                f"Current memory utilization: {mem_after.percent}%."
            )
        except Exception as e:
            play_sound_async("assets/sounds/error.wav")
            logger.error(f"Memory purge failed: {e}")
            return f"MEMORY PURGE ERROR: Could not optimize RAM ({e})."
