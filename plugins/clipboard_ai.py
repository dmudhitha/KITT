"""
Clipboard AI Assistant Plugin for VANGUARD AI Assistant.
Reads copied desktop clipboard content and generates concise AI summaries.
"""
import os
import subprocess
import tkinter as tk
import logging
from typing import List, Dict, Any
from commands import BasePlugin
from utils import play_sound_async

logger = logging.getLogger("vanguard.commands.clipboard_ai")


class ClipboardAIPlugin(BasePlugin):
    """Executes AI processing and summarization on copied desktop clipboard text."""

    @property
    def name(self) -> str:
        return "ClipboardAI"

    @property
    def description(self) -> str:
        return "Reads copied desktop clipboard text and returns concise AI summaries."

    @property
    def commands(self) -> List[str]:
        return ["summarize clipboard", "read clipboard", "explain clipboard", "clipboard"]

    def execute(self, trigger: str, args: str, context: Dict[str, Any]) -> str:
        text = self._get_clipboard_text()
        if not text or not text.strip():
            play_sound_async("assets/sounds/error.wav")
            return "CLIPBOARD NOTICE: Desktop clipboard is empty or contains non-text content."

        play_sound_async("assets/sounds/scan.wav")
        clean_text = text.strip()
        word_count = len(clean_text.split())
        logger.info(f"Retrieved {word_count} word(s) from desktop clipboard.")

        # Provide a quick summary output
        snippet = clean_text[:200] + ("..." if len(clean_text) > 200 else "")
        return f"CLIPBOARD CONTENT RETRIEVED ({word_count} words): \"{snippet}\""

    def _get_clipboard_text(self) -> str:
        """Retrieves text from system clipboard using TK or xclip/xsel fallback."""
        try:
            r = tk.Tk()
            r.withdraw()
            clip_text = r.clipboard_get()
            r.destroy()
            return clip_text
        except Exception:
            pass

        for cmd in [["xclip", "-o", "-selection", "clipboard"], ["xsel", "-b", "-o"]]:
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=1)
                if res.returncode == 0 and res.stdout:
                    return res.stdout
            except Exception:
                continue

        return ""
