"""
LED Scanner Module for VANGUARD AI Assistant.
Implements the iconic Knight Rider horizontal LED scan animation with trail decay and multiple modes.
"""
import logging
from typing import List
import tkinter as tk
import customtkinter as ctk

logger = logging.getLogger("vanguard.scanner")


class LedScanner(ctk.CTkFrame):
    """
    Futuristic LED Scanner widget.
    Animates a set of LED segments with trailing decay effects and multiple visual modes.
    """

    def __init__(
        self,
        parent,
        num_segments: int = 16,
        bg_color: str = "#030303",
        border_color: str = "#330000",
        **kwargs
    ):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.num_segments = num_segments
        self.canvas_bg = bg_color
        self.border_color = border_color

        # Animation states
        self.intensities = [0.0] * num_segments
        self.position = 0.0
        self.direction = 1  # 1 for right, -1 for left
        self.animation_running = False
        self.mode = "scan"  # "scan", "think", "talk", "off"
        self.talk_amplitude = 0.0  # Used to modulate LED heights when talking

        # Layout Canvas
        self.canvas = tk.Canvas(
            self,
            bg=self.canvas_bg,
            highlightthickness=1,
            highlightbackground=self.border_color,
            bd=0
        )
        self.canvas.pack(fill="both", expand=True)

        # Bind resize event to recalculate drawing dimensions
        self.canvas.bind("<Configure>", lambda e: self.draw())

    def start(self) -> None:
        """Starts the animation loop."""
        if not self.animation_running:
            self.animation_running = True
            logger.info("LED Scanner animation started.")
            self._tick()

    def stop(self) -> None:
        """Stops the animation loop."""
        self.animation_running = False
        logger.info("LED Scanner animation stopped.")

    def set_mode(self, mode: str) -> None:
        """Changes the active scanner animation behavior."""
        valid_modes = ["scan", "think", "talk", "off"]
        if mode in valid_modes:
            self.mode = mode
            logger.debug(f"LED Scanner mode changed to: {mode}")
            if mode == "off":
                self.intensities = [0.0] * self.num_segments
                self.draw()
        else:
            logger.warning(f"Invalid scanner mode requested: {mode}")

    def set_talk_amplitude(self, amplitude: float) -> None:
        """Sets simulated voice volume amplitude for voice-modulated mode."""
        self.talk_amplitude = min(max(amplitude, 0.0), 1.0)

    def _tick(self) -> None:
        """Main animation loop tick."""
        if not self.animation_running:
            return

        decay_factor = 0.78  # Lower means faster fading, creating a shorter trail

        # 1. Apply decay to all segments
        self.intensities = [val * decay_factor for val in self.intensities]

        # 2. Update state based on current mode
        if self.mode == "scan":
            self.position += self.direction * 0.65  # Speed coefficient
            pos_int = int(round(self.position))
            
            # Boundary detection and reverse direction
            if pos_int >= self.num_segments - 1:
                self.direction = -1
                self.position = float(self.num_segments - 1)
            elif pos_int <= 0:
                self.direction = 1
                self.position = 0.0
                
            # Light up active cursor segment
            actual_idx = max(0, min(pos_int, self.num_segments - 1))
            self.intensities[actual_idx] = 1.0

        elif self.mode == "think":
            # Bounding pulses scanning inward from edges, crossing at center
            self.position += self.direction * 0.5
            pos_int = int(round(self.position))
            
            half_seg = self.num_segments // 2
            if pos_int >= half_seg - 1:
                self.direction = -1
                self.position = float(half_seg - 1)
            elif pos_int <= 0:
                self.direction = 1
                self.position = 0.0
                
            # Set symmetrical scanner bars
            idx_left = max(0, min(pos_int, half_seg - 1))
            idx_right = self.num_segments - 1 - idx_left
            self.intensities[idx_left] = 1.0
            self.intensities[idx_right] = 1.0

        elif self.mode == "talk":
            # Audio amplitude modulation from center outwards
            center = self.num_segments / 2.0
            import random
            # Add small random jitter for organic feel
            amp = self.talk_amplitude + random.uniform(-0.1, 0.1)
            amp = min(max(amp, 0.0), 1.0)
            
            for i in range(self.num_segments):
                dist = abs(i - center + 0.5)
                # Falloff function: center is brightest, edges are dim
                factor = max(0.0, 1.0 - (dist / (self.num_segments / 2.0)))
                val = amp * factor
                # Maintain the peak or decay
                self.intensities[i] = max(self.intensities[i] * 0.85, val)

        # 3. Redraw frame
        self.draw()

        # Schedule next tick (target ~30 fps to keep UI thread light but smooth)
        self.after(33, self._tick)

    def draw(self) -> None:
        """Draws LED blocks on canvas based on active intensities and window sizing."""
        self.canvas.delete("all")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width <= 1 or height <= 1:
            return

        spacing = 4
        total_gaps_width = spacing * (self.num_segments + 1)
        segment_width = (width - total_gaps_width) / self.num_segments

        for i in range(self.num_segments):
            intensity = self.intensities[i]
            
            # 1. Compute segment bounding box
            x1 = spacing + i * (segment_width + spacing)
            x2 = x1 + segment_width
            
            # Shrink height slightly depending on intensity to add dynamic pulse look
            padding_y = (height * 0.1)
            if self.mode == "talk":
                # Scale segment height based on intensity
                padding_y = (height * 0.45) * (1.0 - intensity) + (height * 0.05)
                
            y1 = padding_y
            y2 = height - padding_y

            # 2. Determine color gradient (Black to Neon Red)
            red_val = int(255 * intensity)
            red_val = max(10, min(red_val, 255))
            
            # Background glowing color
            hex_color = f"#{red_val:02x}0000"
            
            # 3. Draw segment backplane
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=hex_color,
                outline=f"#{min(red_val + 20, 255):02x}0000" if intensity > 0.1 else "#1A0000",
                width=1
            )
            
            # 4. Draw bright center core ("filament" effect) for glowing neon aesthetic
            if intensity > 0.4:
                core_padding_x = segment_width * 0.25
                core_padding_y = (y2 - y1) * 0.3
                cx1 = x1 + core_padding_x
                cx2 = x2 - core_padding_x
                cy1 = y1 + core_padding_y
                cy2 = y2 - core_padding_y
                
                # Orange/White core for bright illumination simulation
                core_intensity = int(255 * (intensity - 0.4) / 0.6)
                core_color = f"#FF{core_intensity:02x}{core_intensity:02x}"
                self.canvas.create_rectangle(
                    cx1, cy1, cx2, cy2,
                    fill=core_color,
                    outline="",
                    width=0
                )
