"""
System Process and Application Killer Plugin for VANGUARD AI Assistant.
Safely terminates target OS processes and application instances by name or PID.
"""
import os
import psutil
import logging
from typing import List, Dict, Any
from commands import BasePlugin
from utils import play_sound_async

logger = logging.getLogger("vanguard.commands.process_killer")


class ProcessKillerPlugin(BasePlugin):
    """Executes target process termination operations."""

    @property
    def name(self) -> str:
        return "ProcessKiller"

    @property
    def description(self) -> str:
        return "Terminates target system background processes or applications by name."

    @property
    def commands(self) -> List[str]:
        return ["kill process", "close app", "terminate process", "kill app", "close application"]

    def execute(self, trigger: str, args: str, context: Dict[str, Any]) -> str:
        target_name = args.strip().lower()
        if not target_name:
            play_sound_async("assets/sounds/error.wav")
            return "PROCESS KILLER ERROR: Specify a target application or process name (e.g., 'kill process chrome')."

        killed_pids = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                pname = proc.info['name'].lower()
                if target_name in pname:
                    pid = proc.info['pid']
                    p = psutil.Process(pid)
                    p.terminate()
                    killed_pids.append(f"{proc.info['name']} (PID {pid})")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        if not killed_pids:
            play_sound_async("assets/sounds/error.wav")
            return f"PROCESS KILLER NOTICE: No active processes matching '{target_name}' were found."

        play_sound_async("assets/sounds/plugin.wav")
        summary = ", ".join(killed_pids[:3])
        logger.info(f"Terminated matching process(es): {summary}")
        return f"SYSTEM DIRECTIVE EXECUTED: Terminated {len(killed_pids)} process instance(s) matching '{target_name}': [{summary}]."
