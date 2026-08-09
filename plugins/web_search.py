"""
Live Web Search and News Headlines Plugin for VANGUARD AI Assistant.
Parses live web search results and news headlines from DuckDuckGo.
"""
import re
import urllib.parse
import urllib.request
import logging
from typing import List, Dict, Any
from commands import BasePlugin
from utils import play_sound_async

logger = logging.getLogger("vanguard.commands.web_search")


class WebSearchPlugin(BasePlugin):
    """Executes live web searches and news headline retrieval."""

    @property
    def name(self) -> str:
        return "WebSearch"

    @property
    def description(self) -> str:
        return "Fetches live web search results and news headlines."

    @property
    def commands(self) -> List[str]:
        return ["search web", "news updates", "web search", "latest news"]

    def execute(self, trigger: str, args: str, context: Dict[str, Any]) -> str:
        query = args.strip() if args.strip() else "latest artificial intelligence news"
        play_sound_async("assets/sounds/scan.wav")
        logger.info(f"Executing web search for query: '{query}'...")

        try:
            encoded = urllib.parse.quote(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded}"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) VANGUARD/1.0"}
            )
            with urllib.request.urlopen(req, timeout=4) as response:
                html = response.read().decode("utf-8", errors="ignore")

            # Extract result snippets from HTML using regex
            snippets = re.findall(r'<a class="result__snippet[^>]*>(.*?)</a>', html, re.DOTALL)
            clean_snippets = []
            for s in snippets:
                clean_text = re.sub(r'<[^>]+>', '', s).strip()
                if clean_text:
                    clean_snippets.append(clean_text)
                if len(clean_snippets) >= 3:
                    break

            if not clean_snippets:
                play_sound_async("assets/sounds/error.wav")
                return f"WEB SEARCH NOTICE: Search completed for '{query}', but no text snippets were extracted."

            play_sound_async("assets/sounds/plugin.wav")
            summary = " | ".join(clean_snippets)
            return f"LIVE WEB SEARCH RESULTS ({len(clean_snippets)} snippets): {summary[:300]}..."
        except Exception as e:
            play_sound_async("assets/sounds/error.wav")
            logger.error(f"Web search failed: {e}")
            return f"WEB SEARCH ERROR: Could not complete search query ({e})."
