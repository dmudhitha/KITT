"""
Log and Memory Query Search Plugin for VANGUARD AI Assistant.
Searches SQLite database memory and system log files for matching directive terms.
"""
import os
import sqlite3
import logging
from typing import List, Dict, Any
from commands import BasePlugin
from utils import play_sound_async

logger = logging.getLogger("vanguard.commands.log_search")


class LogSearchPlugin(BasePlugin):
    """Executes query searches across SQLite conversation memory and system logs."""

    @property
    def name(self) -> str:
        return "LogSearch"

    @property
    def description(self) -> str:
        return "Searches SQLite memory history and system log files for keyword queries."

    @property
    def commands(self) -> List[str]:
        return ["search logs", "search memory", "find in logs", "history search"]

    def execute(self, trigger: str, args: str, context: Dict[str, Any]) -> str:
        query = args.strip().lower()
        if not query:
            play_sound_async("assets/sounds/error.wav")
            return "LOG SEARCH ERROR: Please specify a search query (e.g., 'search logs error' or 'search memory weather')."

        play_sound_async("assets/sounds/scan.wav")
        results = []

        # 1. Search SQLite Database memory.db
        db_path = "database/memory.db"
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT role, message, timestamp FROM conversations WHERE LOWER(message) LIKE ? ORDER BY id DESC LIMIT 3",
                    (f"%{query}%",)
                )
                db_rows = cursor.fetchall()
                conn.close()
                for role, msg, ts in db_rows:
                    results.append(f"[MEMORY {role.upper()}] ({ts[:19]}): {msg[:80]}")
            except Exception as e:
                logger.error(f"DB memory search failed: {e}")

        # 2. Search logs/system.log & logs/commands.log
        for log_file in ["logs/system.log", "logs/commands.log"]:
            if os.path.exists(log_file):
                try:
                    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                        matches = [line.strip() for line in lines if query in line.lower()]
                        for line in matches[-3:]:
                            results.append(f"[{os.path.basename(log_file).upper()}]: {line[:90]}")
                except Exception as e:
                    logger.error(f"Log file search failed for {log_file}: {e}")

        if not results:
            return f"LOG QUERY COMPLETE: No entries matching '{query}' were found."

        summary = " | ".join(results[:4])
        return f"LOG QUERY COMPLETE ({len(results)} matches found): {summary}"
