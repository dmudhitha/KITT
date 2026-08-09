"""
Utilities module for VANGUARD AI Assistant.
Provides custom logging setup and thread-safe messaging helpers.
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional, List


class FuturisticFormatter(logging.Formatter):
    """Custom formatter to style logs with a futuristic system terminal look."""
    
    GREY = "\033[90m"
    CYAN = "\033[36m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    BOLD_RED = "\033[1;31m"
    RESET = "\033[0m"
    
    FORMAT = "[%(asctime)s] [%(name)s] [%(levelname)s] >> %(message)s"

    FORMATS = {
        logging.DEBUG: GREY + FORMAT + RESET,
        logging.INFO: CYAN + FORMAT + RESET,
        logging.WARNING: YELLOW + FORMAT + RESET,
        logging.ERROR: RED + FORMAT + RESET,
        logging.CRITICAL: BOLD_RED + FORMAT + RESET
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno, self.FORMAT)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def setup_logging(
    log_dir: str = "logs",
    log_level_str: str = "INFO",
    log_to_file: bool = True,
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 3
) -> logging.Logger:
    """Configures the root logger with futuristic console logs and rotating file logs."""
    os.makedirs(log_dir, exist_ok=True)
    
    # Resolve log level
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear any existing handlers to avoid duplicates
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(FuturisticFormatter())
    root_logger.addHandler(console_handler)
    
    # File Handler
    if log_to_file:
        system_log_path = os.path.join(log_dir, "system.log")
        file_handler = RotatingFileHandler(
            system_log_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(
            "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
    # Separate loggers for conversations and commands
    _setup_specific_logger("vanguard.conversations", os.path.join(log_dir, "conversations.log"), log_level)
    _setup_specific_logger("vanguard.commands", os.path.join(log_dir, "commands.log"), log_level)

    logger = logging.getLogger("vanguard")
    logger.info("VANGUARD system logging initialized.")
    return logger


def _setup_specific_logger(name: str, log_path: str, level: int) -> None:
    """Helper to set up a dedicated logger file output (e.g., for chat transcripts)."""
    sub_logger = logging.getLogger(name)
    sub_logger.setLevel(level)
    sub_logger.propagate = False  # Avoid duplicates in root logger file
    
    # Clean previous handlers
    sub_logger.handlers.clear()
    
    # File Handler
    file_handler = RotatingFileHandler(log_path, maxBytes=5*1024*1024, backupCount=3, encoding="utf-8")
    file_formatter = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(file_formatter)
    sub_logger.addHandler(file_handler)
    
    # Also forward to custom console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(FuturisticFormatter())
    sub_logger.addHandler(console_handler)


def generate_sine_wav(
    filepath: str,
    frequencies: List[float],
    duration: float = 0.2,
    sample_rate: int = 22050
) -> None:
    """
    Generates a synthesized multi-frequency tone sequence and saves it as a WAV file.
    Does not overwrite if the file already exists.
    """
    if os.path.exists(filepath):
        return

    import wave
    import struct
    import math

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    num_samples = int(duration * sample_rate)

    try:
        with wave.open(filepath, "w") as wav_file:
            # 1 channel, 2 bytes per sample (16-bit), sample_rate
            wav_file.setparams((1, 2, sample_rate, num_samples, "NONE", "not compressed"))

            for i in range(num_samples):
                t = float(i) / sample_rate
                # Blend frequencies
                val = 0.0
                for freq in frequencies:
                    # Slide frequency slightly over time to make it sound like a synth sweep
                    slide = (freq * 0.9) + (freq * 0.2 * (t / duration))
                    val += math.sin(2.0 * math.pi * slide * t)
                
                # Average and scale to 16-bit signed int
                val = (val / len(frequencies)) * 32767.0 * 0.8  # 0.8 volume scale
                data = struct.pack("<h", int(val))
                wav_file.writeframesraw(data)
        logging.getLogger("vanguard").info(f"Synthesized tone file: {filepath}")
    except Exception as e:
        logging.getLogger("vanguard").error(f"Failed to generate synth tone: {e}")


def play_sound_async(filepath: str) -> None:
    """Plays a sound file in a background daemon thread so it is completely non-blocking."""
    import threading
    threading.Thread(target=_play_sound_worker, args=(filepath,), daemon=True).start()


def _play_sound_worker(filepath: str) -> None:
    """Worker thread that initializes pygame mixer and plays a sound."""
    if not os.path.exists(filepath):
        return

    import pygame
    try:
        # Hide pygame hello message
        os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        sound = pygame.mixer.Sound(filepath)
        channel = sound.play()
        # Wait for sound to finish playing before exiting thread
        if channel:
            while channel.get_busy():
                time_sleep(0.05)
    except Exception as e:
        # Fall back silently if sound card is unavailable
        logging.getLogger("vanguard").debug(f"Audio device playback bypassed: {e}")


def time_sleep(seconds: float) -> None:
    """Tiny helper to sleep without blocking global namespaces."""
    import time
    time.sleep(seconds)


def ensure_default_sounds() -> None:
    """Generates all futuristic sci-fi soundboard audio files if not present."""
    sound_dir = "assets/sounds"
    generate_sine_wav(os.path.join(sound_dir, "boot.wav"), [440.0, 880.0, 1760.0], duration=0.4)
    generate_sine_wav(os.path.join(sound_dir, "shutdown.wav"), [1760.0, 880.0, 440.0], duration=0.4)
    generate_sine_wav(os.path.join(sound_dir, "wake.wav"), [1200.0, 1600.0], duration=0.15)
    generate_sine_wav(os.path.join(sound_dir, "plugin.wav"), [880.0, 1320.0, 1760.0], duration=0.2)
    generate_sine_wav(os.path.join(sound_dir, "calc.wav"), [1000.0, 1500.0], duration=0.1)
    generate_sine_wav(os.path.join(sound_dir, "error.wav"), [300.0, 220.0], duration=0.3)
    generate_sine_wav(os.path.join(sound_dir, "scan.wav"), [600.0, 900.0, 1200.0], duration=0.25)


def setup_autostart(enable: bool = True) -> bool:
    """Configures desktop autostart entry for VANGUARD on system boot."""
    import sys
    try:
        autostart_dir = os.path.expanduser("~/.config/autostart")
        desktop_file = os.path.join(autostart_dir, "vanguard.desktop")
        
        if not enable:
            if os.path.exists(desktop_file):
                os.remove(desktop_file)
            return True
            
        os.makedirs(autostart_dir, exist_ok=True)
        main_py_path = os.path.abspath("main.py")
        python_bin = sys.executable
        
        content = f"""[Desktop Entry]
Type=Application
Name=VANGUARD AI Assistant
Comment=Vehicle Autonomous Network & General Utility Assistant
Exec={python_bin} {main_py_path} --autostart
Icon=utilities-terminal
Terminal=false
Categories=Utility;
X-GNOME-Autostart-enabled=true
"""
        with open(desktop_file, "w", encoding="utf-8") as f:
            f.write(content)
        logging.getLogger("vanguard").info(f"System autostart entry updated: {desktop_file}")
        return True
    except Exception as e:
        logging.getLogger("vanguard").error(f"Autostart setup failed: {e}")
        return False
