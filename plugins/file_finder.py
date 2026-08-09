"""
Desktop File Finder Plugin for VANGUARD AI Assistant.
Searches user workspace and home directories for matching filenames.
"""
import os
import logging
from typing import List, Dict, Any
from commands import BasePlugin
from utils import play_sound_async

logger = logging.getLogger("vanguard.commands.file_finder")


class FileFinderPlugin(BasePlugin):
    """Searches local filesystem for target filenames."""

    @property
    def name(self) -> str:
        return "FileFinder"

    @property
    def description(self) -> str:
        return "Locates target files across local user workspace directories."

    @property
    def commands(self) -> List[str]:
        return ["find file", "locate file", "search file", "open file"]

    def execute(self, trigger: str, args: str, context: Dict[str, Any]) -> str:
        query = args.strip().lower()
        if not query:
            play_sound_async("assets/sounds/error.wav")
            return "FILE FINDER ERROR: Specify a target filename to search for (e.g., 'find file dashboard.jpg')."

        play_sound_async("assets/sounds/scan.wav")
        search_dirs = [os.getcwd(), os.path.expanduser("~")]
        matches = []

        for sdir in search_dirs:
            if not os.path.exists(sdir):
                continue
            for root, _, files in os.walk(sdir):
                # Skip hidden directories like .git, .cache
                if any(part.startswith(".") for part in root.split(os.sep)):
                    continue
                for f in files:
                    if query in f.lower():
                        full_path = os.path.join(root, f)
                        matches.append(full_path)
                        if len(matches) >= 3:
                            break
                if len(matches) >= 3:
                    break
            if len(matches) >= 3:
                break

        if not matches:
            play_sound_async("assets/sounds/error.wav")
            return f"FILE FINDER NOTICE: No files matching '{query}' were located."

        play_sound_async("assets/sounds/plugin.wav")
        summary = " | ".join(matches)
        logger.info(f"File search located {len(matches)} match(es) for '{query}'.")
        return f"FILE FINDER DIRECTIVE COMPLETE ({len(matches)} matches located): {summary}"
