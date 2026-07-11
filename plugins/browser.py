"""
Web Browser Plugin for VANGUARD.
"""
import webbrowser
import urllib.parse
from typing import List, Dict, Any
from commands import BasePlugin


class BrowserPlugin(BasePlugin):
    """Launches the default web browser for target websites or web searches."""

    @property
    def name(self) -> str:
        return "BrowserLauncher"

    @property
    def description(self) -> str:
        return "Launches default web browser to open pages or search the web."

    @property
    def commands(self) -> List[str]:
        return ["open browser", "open web", "browse"]

    def execute(self, trigger: str, args: str, context: Dict[str, Any]) -> str:
        if not args:
            url = "https://www.google.com"
            webbrowser.open(url)
            return f"Secure link initialized. Opening default interface index: {url}"
            
        args_clean = args.strip()
        
        # Check if the argument is a URL or search query
        if "." in args_clean and " " not in args_clean:
            # Looks like a domain
            url = args_clean
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
        else:
            # Treat as search query
            query_encoded = urllib.parse.quote_plus(args_clean)
            url = f"https://www.google.com/search?q={query_encoded}"
            
        webbrowser.open(url)
        return f"Secure link established. Routing browser core to: {url}"
