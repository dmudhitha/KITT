"""
Configuration and Memory Backup / Restore Plugin for VANGUARD AI Assistant.
Archives settings, SQLite memory database, and user configurations into zip backups.
"""
import os
import time
import zipfile
import logging
from typing import List, Dict, Any
from commands import BasePlugin
from utils import play_sound_async

logger = logging.getLogger("vanguard.commands.backup")


class SystemBackupPlugin(BasePlugin):
    """Executes zip archive backups of configuration settings and SQLite memory."""

    @property
    def name(self) -> str:
        return "SystemBackup"

    @property
    def description(self) -> str:
        return "Archives system settings and SQLite conversation database into zip backup packages."

    @property
    def commands(self) -> List[str]:
        return ["backup system", "restore system", "backup configuration", "export memory backup"]

    def execute(self, trigger: str, args: str, context: Dict[str, Any]) -> str:
        try:
            backups_dir = "assets/backups"
            os.makedirs(backups_dir, exist_ok=True)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"vanguard_backup_{timestamp}.zip"
            filepath = os.path.join(backups_dir, filename)

            files_to_backup = [
                "config/settings.json",
                "database/memory.db",
                "logs/system.log",
                "logs/commands.log"
            ]

            archived_count = 0
            with zipfile.ZipFile(filepath, "w", zipfile.ZIP_DEFLATED) as zipf:
                for fpath in files_to_backup:
                    if os.path.exists(fpath):
                        zipf.write(fpath, arcname=fpath)
                        archived_count += 1

            play_sound_async("assets/sounds/plugin.wav")
            logger.info(f"System backup package created: {filepath} ({archived_count} files)")
            return f"SYSTEM BACKUP COMPLETE: Archived {archived_count} files into '{filepath}'."
        except Exception as e:
            play_sound_async("assets/sounds/error.wav")
            logger.error(f"System backup failed: {e}")
            return f"BACKUP ERROR: Could not create backup archive ({e})."
