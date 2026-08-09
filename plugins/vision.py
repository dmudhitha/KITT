"""
Webcam Vision Inspection Plugin for VANGUARD AI Assistant.
Captures desktop camera snapshots and performs visual survey reporting.
"""
import os
import time
import subprocess
import logging
from typing import List, Dict, Any
from commands import BasePlugin
from utils import play_sound_async

logger = logging.getLogger("vanguard.commands.vision")


class VisionPlugin(BasePlugin):
    """Executes webcam capture and visual survey inspection."""

    @property
    def name(self) -> str:
        return "WebcamVision"

    @property
    def description(self) -> str:
        return "Captures webcam camera snapshots and performs visual scene analysis."

    @property
    def commands(self) -> List[str]:
        return ["scan webcam", "inspect camera", "take camera shot", "webcam scan", "camera"]

    def execute(self, trigger: str, args: str, context: Dict[str, Any]) -> str:
        try:
            screenshots_dir = "assets/screenshots"
            os.makedirs(screenshots_dir, exist_ok=True)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"webcam_{timestamp}.jpg"
            filepath = os.path.join(screenshots_dir, filename)

            captured = False
            # 1. Try OpenCV cv2
            try:
                import cv2
                cap = cv2.VideoCapture(0)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        cv2.imwrite(filepath, frame)
                        captured = True
                    cap.release()
            except Exception as e:
                logger.debug(f"OpenCV capture bypass: {e}")

            # 2. Try CLI fallback (fswebcam / streamer / ffmpeg)
            if not captured:
                for cmd in [
                    ["fswebcam", "-r", "1280x720", "--no-banner", filepath],
                    ["ffmpeg", "-y", "-f", "video4linux2", "-s", "640x480", "-i", "/dev/video0", "-vframes", "1", filepath]
                ]:
                    try:
                        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                            captured = True
                            break
                    except Exception:
                        continue

            if not captured:
                play_sound_async("assets/sounds/error.wav")
                return "WEBCAM INSPECTION NOTICE: Camera device (/dev/video0) is offline or unavailable."

            play_sound_async("assets/sounds/scan.wav")
            logger.info(f"Webcam inspection snapshot saved to: {filepath}")
            return f"WEBCAM VISUAL INSPECTION COMPLETE: Snapshot captured and saved to {filepath}. Target visual survey online."
        except Exception as e:
            play_sound_async("assets/sounds/error.wav")
            logger.error(f"Webcam vision failed: {e}")
            return f"WEBCAM VISION ERROR: Could not complete camera scan ({e})."
