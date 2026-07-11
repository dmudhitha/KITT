"""
Commands and Plugin Manager Module for VANGUARD.
Establishes the BasePlugin model and dynamically loads command plugins from the plugins/ directory.
"""
import os
import sys
import time
import logging
import datetime
import importlib.util
import webbrowser
from typing import List, Dict, Any, Optional

logger = logging.getLogger("vanguard.commands")


class BasePlugin:
    """Base class that all VANGUARD command plugins must inherit from."""

    @property
    def name(self) -> str:
        """Descriptive name of the plugin."""
        raise NotImplementedError

    @property
    def description(self) -> str:
        """Short summary of what the plugin does."""
        raise NotImplementedError

    @property
    def commands(self) -> List[str]:
        """List of lowercase trigger words/phrases matched against user commands."""
        raise NotImplementedError

    def execute(self, trigger: str, args: str, context: Dict[str, Any]) -> str:
        """
        Executes command logic.
        Returns a string response displayed in the chat and spoken.
        """
        raise NotImplementedError


class PluginManager:
    """Loads, registers, and routes commands to registered plugins and built-ins."""

    def __init__(self, config_manager, db_manager):
        self.config = config_manager
        self.db = db_manager
        self.plugins: Dict[str, BasePlugin] = {}
        self.trigger_map: Dict[str, BasePlugin] = {}

        # Load built-ins and plugins
        self._register_builtins()
        self.load_plugins()

    def register_plugin(self, plugin: BasePlugin) -> None:
        """Registers a plugin instance and hooks its triggers to the map."""
        self.plugins[plugin.name] = plugin
        for cmd in plugin.commands:
            cmd_lower = cmd.lower().strip()
            self.trigger_map[cmd_lower] = plugin
            logger.debug(f"Hooked command trigger: '{cmd_lower}' -> {plugin.name}")

    def load_plugins(self, plugins_dir: str = "plugins") -> None:
        """Scans plugins_dir and dynamically imports subclassed BasePlugin modules."""
        os.makedirs(plugins_dir, exist_ok=True)

        for filename in os.listdir(plugins_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = filename[:-3]
                file_path = os.path.join(plugins_dir, filename)

                try:
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[module_name] = module
                        spec.loader.exec_module(module)

                        # Look for subclasses of BasePlugin in module
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if (
                                isinstance(attr, type)
                                and issubclass(attr, BasePlugin)
                                and attr is not BasePlugin
                            ):
                                plugin_instance = attr()
                                self.register_plugin(plugin_instance)
                                logger.info(f"Loaded external plugin: {plugin_instance.name}")
                except Exception as e:
                    logger.error(f"Failed to dynamically load plugin module '{module_name}': {e}")

    def parse_and_execute(self, user_input: str, context: Dict[str, Any]) -> Optional[str]:
        """
        Parses user input to see if it matches any registered command.
        Executes matches locally, bypassing LLM. Returns response string or None.
        """
        input_cleaned = user_input.lower().strip()
        start_time = time.time()

        for trigger, plugin in self.trigger_map.items():
            # Check for exact trigger matches, or prefix matches (e.g., 'open browser google.com')
            if input_cleaned == trigger or input_cleaned.startswith(trigger + " "):
                args = input_cleaned[len(trigger):].strip()
                logger.info(f"Command trigger matched: '{trigger}' delegating to '{plugin.name}'")

                try:
                    response = plugin.execute(trigger, args, context)
                    duration_ms = int((time.time() - start_time) * 1000)
                    self.db.log_command(trigger, args, "success", duration_ms)
                    return response
                except Exception as e:
                    logger.error(f"Error executing command plugin '{plugin.name}': {e}")
                    duration_ms = int((time.time() - start_time) * 1000)
                    self.db.log_command(trigger, args, "failure", duration_ms)
                    return f"VANGUARD CMD ERROR: Failed to execute internal command. Details: {e}"

        return None

    def _register_builtins(self) -> None:
        """Registers default core system command utilities."""
        self.register_plugin(SystemCorePlugin())


# Built-in Core Plugin
class SystemCorePlugin(BasePlugin):
    """Built-in command plugin for VANGUARD core utilities."""

    @property
    def name(self) -> str:
        return "SystemCore"

    @property
    def description(self) -> str:
        return "VANGUARD Core system utility operations (help, clock, mute, shutdown)"

    @property
    def commands(self) -> List[str]:
        return ["help", "time", "date", "mute", "unmute", "wake up", "shutdown", "diagnostics"]

    def execute(self, trigger: str, args: str, context: Dict[str, Any]) -> str:
        ui_app = context.get("ui")
        voice_rec = context.get("voice_rec")

        if trigger == "help":
            manager = context.get("manager")
            lines = ["--- AVAILABLE COMMAND MODULES ---"]
            if manager:
                for p_name, p in manager.plugins.items():
                    lines.append(f"* {p.name}: {p.description}")
                    lines.append(f"  Triggers: {', '.join(p.commands)}")
            return "\n".join(lines)

        elif trigger == "time":
            return f"The current internal clock reads: {datetime.datetime.now().strftime('%I:%M %p')}."

        elif trigger == "date":
            return f"Today's star date coordinate is: {datetime.datetime.now().strftime('%A, %B %d, %Y')}."

        elif trigger in ["mute", "unmute", "wake up"]:
            if trigger == "mute":
                if voice_rec:
                    voice_rec.set_mute(True)
                if ui_app:
                    ui_app.draw_voice_indicator("gray")
                return "Acoustic mute mode activated. Sub-vocal sensors deactivated."
            else:
                if voice_rec:
                    voice_rec.set_mute(False)
                if ui_app:
                    ui_app.draw_voice_indicator("gray")
                return "Secure voice routing protocols activated. Awaiting verbal commands."

        elif trigger == "diagnostics":
            diag = context.get("diagnostics")
            if diag:
                report = diag.get_diagnostics_report()
                temp_str = f"{report['cpu_temp']:.1f}°C" if report["cpu_temp"] else "N/A"
                net_str = "ONLINE" if report["network_online"] else "OFFLINE"
                bat_str = f"{report['battery']['percent']}%" if report["battery"]["present"] else "AC POWER"
                return (
                    f"VANGUARD SECURE STATUS REPORT:\n"
                    f"- CPU Load: {report['cpu_percent']}%\n"
                    f"- RAM Capacity: {report['ram_percent']}%\n"
                    f"- Disk Space: {report['disk_percent']}%\n"
                    f"- CPU Core Temp: {temp_str}\n"
                    f"- Power Source: {bat_str}\n"
                    f"- Core Network Link: {net_str}"
                )
            return "Diagnostics engine unavailable."

        elif trigger == "shutdown":
            if ui_app:
                ui_app.after(100, ui_app.trigger_shutdown)
            return "Secure shutdown request recognized. Terminating dashboard core..."

        return f"Core system command '{trigger}' parsed but execution handler is pending."
