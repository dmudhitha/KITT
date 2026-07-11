"""
Weather Plugin for VANGUARD.
"""
import random
from typing import List, Dict, Any
from commands import BasePlugin


class WeatherPlugin(BasePlugin):
    """Provides local or global mockup weather forecasts."""

    @property
    def name(self) -> str:
        return "WeatherTracker"

    @property
    def description(self) -> str:
        return "Simulates local or global weather telemetry feeds."

    @property
    def commands(self) -> List[str]:
        return ["weather", "get weather", "weather report"]

    def execute(self, trigger: str, args: str, context: Dict[str, Any]) -> str:
        city = args.strip().title() if args else "Primary Vector Base"
        
        # Seed generator based on city characters to ensure semi-reproducible values for testing
        hash_seed = sum(ord(c) for c in city)
        random.seed(hash_seed)
        
        temp = random.randint(18, 38)
        humidity = random.randint(40, 95)
        wind_speed = random.randint(5, 30)
        conditions = [
            "Clear Skies / Solar Index Nominal",
            "Scattered Clouds / Visuals Unobstructed",
            "Precipitation Vector Imminent / Rain Shields Advised",
            "High Humidity / Atmospheric Density Elevated",
            "Thermal storm Warning / Electrical Activity Logged"
        ]
        condition = random.choice(conditions)
        
        # Reset seed to avoid corrupting global state
        random.seed(None)

        return (
            f"ENVIRONMENT SURVEY REPORT FOR: {city.upper()}\n"
            f"- Ambient Temperature: {temp}°C\n"
            f"- Relative Humidity: {humidity}%\n"
            f"- Wind Speed: {wind_speed} km/h\n"
            f"- Atmospheric Forecast: {condition}"
        )
