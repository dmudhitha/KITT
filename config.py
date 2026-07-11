"""
Configuration Manager for VANGUARD AI Desktop Assistant.
Handles JSON-based settings load, save, environment override, and validation.
"""
import os
import json
import logging
from typing import Any, Dict
from dotenv import load_dotenv

logger = logging.getLogger("vanguard.config")


class ConfigManager:
    """Manages system configurations and runtime parameters."""

    def __init__(self, config_dir: str = "config", filename: str = "settings.json"):
        self.config_dir = config_dir
        self.config_path = os.path.join(config_dir, filename)
        self.settings: Dict[str, Any] = {}
        
        # Load environment variables (useful for API keys)
        load_dotenv()
        
        self.load_config()

    def load_config(self) -> None:
        """Loads configuration from JSON file. Falls back to defaults if not found."""
        os.makedirs(self.config_dir, exist_ok=True)
        
        if not os.path.exists(self.config_path):
            logger.warning(f"Configuration file not found at {self.config_path}. Reverting to default settings.")
            self.settings = self._get_default_settings()
            self.save_config()
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.settings = json.load(f)
            logger.info("Configuration loaded successfully.")
            self._apply_env_overrides()
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to parse settings JSON: {e}. Rebuilding defaults.")
            self.settings = self._get_default_settings()
            self.save_config()

    def save_config(self) -> bool:
        """Saves current settings back to settings.json."""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
            logger.info("Configuration saved successfully.")
            return True
        except IOError as e:
            logger.error(f"Error saving settings: {e}")
            return False

    def get(self, category: str, key: str, default: Any = None) -> Any:
        """Helper to get nested settings safely."""
        return self.settings.get(category, {}).get(key, default)

    def set(self, category: str, key: str, value: Any) -> None:
        """Set configuration value dynamically and schedule save."""
        if category not in self.settings:
            self.settings[category] = {}
        self.settings[category][key] = value
        self.save_config()

    def _apply_env_overrides(self) -> None:
        """Override configuration with environment variables if present."""
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            if "api" not in self.settings:
                self.settings["api"] = {}
            self.settings["api"]["openai_api_key"] = openai_key
            logger.info("OPENAI_API_KEY overridden from environment.")

    def _get_default_settings(self) -> Dict[str, Any]:
        """Provides fallback configurations."""
        return {
            "api": {
                "provider": "openai",
                "openai_api_key": "",
                "openai_model": "gpt-4-turbo",
                "local_url": "http://localhost:11434/v1",
                "local_model": "llama3",
                "system_prompt": "You are VANGUARD (Vehicle Autonomous Network & General Utility Assistant for Research and Diagnostics). analytical, intelligent, highly capable, and slightly dry."
            },
            "ui": {
                "theme": "dark",
                "accent_color": "#FF0000",
                "bg_color": "#080808",
                "panel_bg_color": "#121212",
                "glow_color": "#FF3333",
                "font_family": "Courier New",
                "fullscreen": False,
                "width": 1024,
                "height": 768
            },
            "voice": {
                "tts_enabled": True,
                "tts_engine": "sapi5",
                "tts_rate": 185,
                "tts_volume": 1.0,
                "tts_voice_index": 0,
                "stt_enabled": True,
                "wake_word": "hey kitt",
                "wake_word_enabled": True,
                "mic_energy_threshold": 300,
                "mic_timeout": 5,
                "mute_mode": False
            },
            "diagnostics": {
                "poll_interval_ms": 1000,
                "cpu_warning_threshold": 80.0,
                "ram_warning_threshold": 85.0
            },
            "logging": {
                "log_level": "INFO",
                "log_to_file": true,
                "max_log_size_bytes": 5242880,
                "backup_count": 3
            }
        }
