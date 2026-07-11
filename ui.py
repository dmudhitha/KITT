"""
User Interface Module for VANGUARD AI Assistant.
Built using CustomTkinter with a futuristic dark/neon HUD aesthetic.
"""
import time
import logging
import datetime
import threading
from typing import Callable, Optional
import tkinter as tk
import customtkinter as ctk
import psutil
from scanner import LedScanner
from diagnostics import SystemDiagnostics
from utils import play_sound_async

logger = logging.getLogger("vanguard.ui")


class VanguardUI(ctk.CTk):
    """Futuristic dashboard UI class for VANGUARD assistant."""

    def __init__(
        self,
        config_manager,
        db_manager,
        on_send_callback: Optional[Callable[[str], None]] = None,
        on_mic_callback: Optional[Callable[[], None]] = None,
        on_shutdown_callback: Optional[Callable[[], None]] = None,
    ):
        super().__init__()
        self.config = config_manager
        self.db = db_manager
        self.diagnostics = SystemDiagnostics()
        self.on_send = on_send_callback
        self.on_mic = on_mic_callback
        self.on_shutdown = on_shutdown_callback

        # Load window configurations
        self.width = self.config.get("ui", "width", 1024)
        self.height = self.config.get("ui", "height", 768)
        self.accent_color = self.config.get("ui", "accent_color", "#FF3333")
        self.bg_color = self.config.get("ui", "bg_color", "#080808")
        self.panel_bg_color = self.config.get("ui", "panel_bg_color", "#121212")
        self.font_family = self.config.get("ui", "font_family", "Courier New")

        # Window parameters
        self.title("VANGUARD SECURE INTERFACE v1.0")
        self.geometry(f"{self.width}x{self.height}")
        self.configure(fg_color=self.bg_color)
        ctk.set_appearance_mode("dark")

        # Application state
        self.is_listening = False
        self.is_thinking = False
        self.boot_complete = False
        self.is_shutting_down = False

        # Key Bindings
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.exit_fullscreen)
        self.protocol("WM_DELETE_WINDOW", self.trigger_shutdown)

        # Build grid layout
        self.grid_columnconfigure(0, weight=1, minsize=260)  # Sidebar diagnostics
        self.grid_columnconfigure(1, weight=3)              # Chat console
        self.grid_rowconfigure(0, weight=0, minsize=100)     # Header
        self.grid_rowconfigure(1, weight=1)                  # Main workspace
        self.grid_rowconfigure(2, weight=0, minsize=50)      # Footer status

        self._build_header()
        self._build_sidebar()
        self._build_chat_panel()
        self._build_footer()

        # Start periodic tasks
        self.update_clock()
        self.update_diagnostics()
        self.animate_telemetry()

        # Trigger startup sequence
        self.after(500, self.run_boot_sequence)

    def _build_header(self) -> None:
        """Constructs the top status header."""
        self.header_frame = ctk.CTkFrame(
            self,
            fg_color=self.panel_bg_color,
            border_color=self.accent_color,
            border_width=1,
            corner_radius=0
        )
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=2)
        self.header_frame.grid_columnconfigure(2, weight=1)

        # 1. Left Title Logo
        self.logo_label = ctk.CTkLabel(
            self.header_frame,
            text="[ V.A.N.G.U.A.R.D. ]",
            font=(self.font_family, 22, "bold"),
            text_color=self.accent_color
        )
        self.logo_label.grid(row=0, column=0, sticky="w", padx=20)

        # 2. Scanner bay
        self.scanner_bay = ctk.CTkFrame(
            self.header_frame,
            fg_color="#030303",
            border_color="#330000",
            border_width=1,
            height=50
        )
        self.scanner_bay.grid(row=0, column=1, sticky="ew", padx=10)
        
        # Live LED Scanner
        self.scanner = LedScanner(
            self.scanner_bay,
            num_segments=16,
            bg_color="#030303",
            border_color="#330000"
        )
        self.scanner.pack(fill="both", expand=True, padx=4, pady=4)

        # 3. Clock and Date
        self.time_date_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.time_date_frame.grid(row=0, column=2, sticky="e", padx=20)

        self.time_label = ctk.CTkLabel(
            self.time_date_frame,
            text="00:00:00",
            font=(self.font_family, 18, "bold"),
            text_color="#00FFFF"
        )
        self.time_label.pack(anchor="e")

        self.date_label = ctk.CTkLabel(
            self.time_date_frame,
            text="1970-01-01",
            font=(self.font_family, 11),
            text_color="#888888"
        )
        self.date_label.pack(anchor="e")

    def _build_sidebar(self) -> None:
        """Constructs the sidebar system diagnostics panel."""
        self.sidebar = ctk.CTkFrame(
            self,
            fg_color=self.panel_bg_color,
            border_color=self.accent_color,
            border_width=1,
            corner_radius=0
        )
        self.sidebar.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))

        # Panel title
        self.sidebar_title = ctk.CTkLabel(
            self.sidebar,
            text="SYS MONITOR",
            font=(self.font_family, 14, "bold"),
            text_color=self.accent_color
        )
        self.sidebar_title.pack(anchor="w", padx=15, pady=(15, 10))

        # CPU Monitor
        self.cpu_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.cpu_frame.pack(fill="x", padx=15, pady=8)
        self.cpu_label = ctk.CTkLabel(
            self.cpu_frame, text="CPU Usage: --%", font=(self.font_family, 11), text_color="#00FFFF"
        )
        self.cpu_label.pack(anchor="w")
        self.cpu_bar = ctk.CTkProgressBar(self.cpu_frame, progress_color=self.accent_color, fg_color="#330000")
        self.cpu_bar.set(0.0)
        self.cpu_bar.pack(fill="x", pady=2)

        # RAM Monitor
        self.ram_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.ram_frame.pack(fill="x", padx=15, pady=8)
        self.ram_label = ctk.CTkLabel(
            self.ram_frame, text="RAM Usage: --%", font=(self.font_family, 11), text_color="#00FFFF"
        )
        self.ram_label.pack(anchor="w")
        self.ram_bar = ctk.CTkProgressBar(self.ram_frame, progress_color=self.accent_color, fg_color="#330000")
        self.ram_bar.set(0.0)
        self.ram_bar.pack(fill="x", pady=2)

        # Disk Monitor
        self.disk_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.disk_frame.pack(fill="x", padx=15, pady=8)
        self.disk_label = ctk.CTkLabel(
            self.disk_frame, text="Disk Space: --%", font=(self.font_family, 11), text_color="#00FFFF"
        )
        self.disk_label.pack(anchor="w")
        self.disk_bar = ctk.CTkProgressBar(self.disk_frame, progress_color=self.accent_color, fg_color="#330000")
        self.disk_bar.set(0.0)
        self.disk_bar.pack(fill="x", pady=2)

        # Extra Diagnostics (Battery, Temp, Network)
        self.extra_diag_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.extra_diag_frame.pack(fill="x", padx=15, pady=8)
        
        self.temp_label = ctk.CTkLabel(
            self.extra_diag_frame, text="CPU Temp: N/A", font=(self.font_family, 11), text_color="#00FFFF"
        )
        self.temp_label.pack(anchor="w", pady=2)

        self.battery_label = ctk.CTkLabel(
            self.extra_diag_frame, text="Battery: AC POWER", font=(self.font_family, 11), text_color="#00FFFF"
        )
        self.battery_label.pack(anchor="w", pady=2)

        self.network_label = ctk.CTkLabel(
            self.extra_diag_frame, text="Network: CHECKING...", font=(self.font_family, 11), text_color="#00FFFF"
        )
        self.network_label.pack(anchor="w", pady=2)

        # Telemetry simulator (Sine sweep screen)
        self.telemetry_title = ctk.CTkLabel(
            self.sidebar,
            text="DIAG TELEMETRY",
            font=(self.font_family, 12, "bold"),
            text_color=self.accent_color
        )
        self.telemetry_title.pack(anchor="w", padx=15, pady=(20, 5))

        self.telemetry_canvas = tk.Canvas(
            self.sidebar,
            bg="#030303",
            highlightthickness=1,
            highlightbackground="#330000",
            height=120
        )
        self.telemetry_canvas.pack(fill="x", padx=15, pady=5)
        self.sweep_index = 0

    def _build_chat_panel(self) -> None:
        """Constructs the chat and input interface."""
        self.chat_panel = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.chat_panel.grid(row=1, column=1, sticky="nsew", padx=(0, 5), pady=(0, 5))
        self.chat_panel.grid_columnconfigure(0, weight=1)
        self.chat_panel.grid_rowconfigure(0, weight=1)        # Textbox log
        self.chat_panel.grid_rowconfigure(1, weight=0, minsize=40)  # Status/Indicator bar
        self.chat_panel.grid_rowconfigure(2, weight=0, minsize=60)  # Inputs

        # 1. Main Terminal Console
        self.console_textbox = ctk.CTkTextbox(
            self.chat_panel,
            fg_color="#050505",
            border_color=self.accent_color,
            border_width=1,
            font=(self.font_family, 12),
            text_color="#FFAAAA",
            state="disabled",
            corner_radius=0
        )
        self.console_textbox.grid(row=0, column=0, sticky="nsew")

        # 2. Status & Animation Bar
        self.status_bar = ctk.CTkFrame(self.chat_panel, fg_color="transparent")
        self.status_bar.grid(row=1, column=0, sticky="ew", pady=5)

        # Voice indicator canvas
        self.indicator_canvas = tk.Canvas(
            self.status_bar,
            bg="#121212",
            width=20,
            height=20,
            highlightthickness=0
        )
        self.indicator_canvas.pack(side="left", padx=(10, 5))
        self.draw_voice_indicator("gray")  # Initial state: Mute/Idle

        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="VANGUARD SYS READY",
            font=(self.font_family, 10, "bold"),
            text_color="#888888"
        )
        self.status_label.pack(side="left", padx=5)

        # Thinking Animation Label
        self.thinking_label = ctk.CTkLabel(
            self.status_bar,
            text="",
            font=(self.font_family, 10, "italic"),
            text_color="#00FFFF"
        )
        self.thinking_label.pack(side="right", padx=15)

        # 3. Input bar
        self.input_frame = ctk.CTkFrame(self.chat_panel, fg_color="transparent")
        self.input_frame.grid(row=2, column=0, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.input_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Enter secure instruction command...",
            font=(self.font_family, 12),
            fg_color="#0A0A0A",
            border_color="#333333",
            border_width=1,
            height=40,
            corner_radius=0
        )
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.input_entry.bind("<Return>", lambda e: self.send_message())
        self.input_entry.configure(state="disabled")  # Disabled during boot sequence

        self.send_button = ctk.CTkButton(
            self.input_frame,
            text="EXECUTE",
            font=(self.font_family, 11, "bold"),
            fg_color="#220000",
            hover_color="#550000",
            border_color=self.accent_color,
            border_width=1,
            text_color=self.accent_color,
            width=100,
            height=40,
            corner_radius=0,
            command=self.send_message
        )
        self.send_button.grid(row=0, column=1, sticky="w", padx=2)
        self.send_button.configure(state="disabled")

        self.mic_button = ctk.CTkButton(
            self.input_frame,
            text="🎤 LISTEN",
            font=(self.font_family, 11, "bold"),
            fg_color="#220000",
            hover_color="#550000",
            border_color=self.accent_color,
            border_width=1,
            text_color=self.accent_color,
            width=100,
            height=40,
            corner_radius=0,
            command=self.toggle_mic
        )
        self.mic_button.grid(row=0, column=2, sticky="w", padx=(2, 0))
        self.mic_button.configure(state="disabled")

    def _build_footer(self) -> None:
        """Constructs the very bottom system bar."""
        self.footer = ctk.CTkFrame(
            self,
            fg_color=self.panel_bg_color,
            border_color="#330000",
            border_width=1,
            corner_radius=0
        )
        self.footer.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=(0, 5))

        self.version_label = ctk.CTkLabel(
            self.footer,
            text="SECURE LINK VERIFIED // SYSTEM INTEGRITY SECURE // ENCRYPTION AES-256",
            font=(self.font_family, 9),
            text_color="#444444"
        )
        self.version_label.pack(side="left", padx=15, pady=5)

        self.mode_label = ctk.CTkLabel(
            self.footer,
            text="MODE: DESKTOP HUD",
            font=(self.font_family, 9, "bold"),
            text_color="#666666"
        )
        self.mode_label.pack(side="right", padx=15, pady=5)

    def draw_voice_indicator(self, color_name: str) -> None:
        """Draws the glowing status indicator based on system state."""
        self.indicator_canvas.delete("all")
        color_map = {
            "gray": ("#333333", "#1A1A1A"),     # Off / Muted
            "red": ("#FF3333", "#660000"),      # Voice Recognition Active / Listening
            "green": ("#33FF33", "#005500"),    # AI speaking / Audio output
            "yellow": ("#FFFF33", "#555500")    # System warning / thinking
        }
        fill, outline = color_map.get(color_name, ("#333333", "#1A1A1A"))
        # Draw glowing outer ring
        self.indicator_canvas.create_oval(2, 2, 18, 18, fill=fill, outline=outline, width=2)

    # UI updates
    def update_clock(self) -> None:
        """Updates date and time labels."""
        now = datetime.datetime.now()
        self.time_label.configure(text=now.strftime("%H:%M:%S"))
        self.date_label.configure(text=now.strftime("%Y-%m-%d"))
        if not self.is_shutting_down:
            self.after(1000, self.update_clock)

    def update_diagnostics(self) -> None:
        """Periodically polls system metrics via SystemDiagnostics."""
        if self.is_shutting_down:
            return

        if self.boot_complete:
            try:
                report = self.diagnostics.get_diagnostics_report()
                
                cpu = report["cpu_percent"]
                ram = report["ram_percent"]
                disk = report["disk_percent"]
                battery = report["battery"]
                network_online = report["network_online"]
                cpu_temp = report["cpu_temp"]

                # 1. Update Core progress bars
                self.cpu_label.configure(text=f"CPU Usage: {cpu}%")
                self.cpu_bar.set(cpu / 100.0)

                self.ram_label.configure(text=f"RAM Usage: {ram}%")
                self.ram_bar.set(ram / 100.0)

                self.disk_label.configure(text=f"Disk Space: {disk}%")
                self.disk_bar.set(disk / 100.0)

                # 2. Update Temperature Label
                if cpu_temp is not None:
                    self.temp_label.configure(text=f"CPU Temp: {cpu_temp:.1f}°C", text_color="#00FFFF")
                else:
                    self.temp_label.configure(text="CPU Temp: N/A", text_color="#888888")

                # 3. Update Battery Label
                if battery.get("present", False):
                    status_icon = "⚡" if battery["power_plugged"] else "🔋"
                    self.battery_label.configure(
                        text=f"Battery: {battery['percent']}% [{status_icon}]",
                        text_color="#00FFFF"
                    )
                else:
                    self.battery_label.configure(text="Battery: AC POWER", text_color="#888888")

                # 4. Update Network Label
                if network_online:
                    self.network_label.configure(text="Network: ONLINE", text_color="#33FF33")
                else:
                    self.network_label.configure(text="Network: OFFLINE", text_color="#FF3333")

                # 5. Dynamic Warning Colors for CPU load
                cpu_threshold = self.config.get("diagnostics", "cpu_warning_threshold", 80.0)
                if cpu > cpu_threshold:
                    self.cpu_bar.configure(progress_color="#FF9900")
                else:
                    self.cpu_bar.configure(progress_color=self.accent_color)
                    
            except Exception as e:
                logger.error(f"Error updating GUI diagnostics: {e}")

        self.after(self.config.get("diagnostics", "poll_interval_ms", 1000), self.update_diagnostics)

    def animate_telemetry(self) -> None:
        """Renders an animated scanning telemetry sine sweep."""
        if self.is_shutting_down:
            return

        self.telemetry_canvas.delete("all")
        width = self.telemetry_canvas.winfo_width()
        height = self.telemetry_canvas.winfo_height()

        if width > 1:
            points = []
            for x in range(0, width, 5):
                # Compose two sine waves for complex radar scan effect
                y1 = math_sine(x, self.sweep_index, width, height)
                points.append((x, y1))
            
            # Draw line
            if len(points) > 1:
                flat_points = [coord for pt in points for coord in pt]
                self.telemetry_canvas.create_line(flat_points, fill="#00FFFF", width=1)
                
            # Draw sweep scanlines
            sweep_x = (self.sweep_index * 4) % width
            self.telemetry_canvas.create_line(sweep_x, 0, sweep_x, height, fill="#FF0000", width=1)

        self.sweep_index += 1
        self.after(50, self.animate_telemetry)

    # Console output utilities
    def console_print(self, text: str, prefix: str = "[SYSTEM] >> ") -> None:
        """Safely inserts structured output into the terminal scrolling textbox."""
        self.console_textbox.configure(state="normal")
        self.console_textbox.insert(tk.END, f"{prefix}{text}\n")
        self.console_textbox.see(tk.END)
        self.console_textbox.configure(state="disabled")

    def console_stream_start(self, prefix: str = "[VANGUARD] >> ") -> None:
        """Begins a streaming insertion block by writing the prefix."""
        self.console_textbox.configure(state="normal")
        self.console_textbox.insert(tk.END, prefix)
        self.console_textbox.see(tk.END)
        self.console_textbox.configure(state="disabled")

    def console_stream_chunk(self, text: str) -> None:
        """Appends a single chunk of streaming text without prefix or newlines."""
        self.console_textbox.configure(state="normal")
        self.console_textbox.insert(tk.END, text)
        self.console_textbox.see(tk.END)
        self.console_textbox.configure(state="disabled")

    def console_stream_end(self) -> None:
        """Finalizes the streaming session by writing a trailing newline."""
        self.console_textbox.configure(state="normal")
        self.console_textbox.insert(tk.END, "\n")
        self.console_textbox.see(tk.END)
        self.console_textbox.configure(state="disabled")

    # Animations: Startup / Boot Sequence
    def run_boot_sequence(self) -> None:
        """Simulates system component initialization sequence."""
        boot_logs = [
            ("INITIALIZING SECURE LINK TO QUANTUM CORE...", 200),
            ("LOAD SUBSYSTEM: CONFIGURATION CONFIGS... OK", 400),
            ("LOAD SUBSYSTEM: SQLITE REPOSITORY LOGS... OK", 700),
            ("LOAD SUBSYSTEM: SPEECH SYNTHESIS ENGINE... OK", 1000),
            ("LOAD SUBSYSTEM: AI LLM HANDLERS... OK", 1300),
            ("WARNING: CLASSIFIED VANGUARD SECURITY ENFORCED", 1600),
            ("VANGUARD ARTIFICIAL INTELLIGENCE CORE ONLINE.", 2000),
        ]

        def step_loader(idx: int):
            if idx < len(boot_logs):
                msg, delay = boot_logs[idx]
                self.console_print(msg)
                
                # Animate diagnostics bar fills during boot
                progress = (idx + 1) / len(boot_logs)
                self.cpu_bar.set(progress * 0.4)
                self.ram_bar.set(progress * 0.3)
                self.disk_bar.set(progress * 0.7)
                
                self.after(delay, lambda: step_loader(idx + 1))
            else:
                self.boot_complete = True
                self.input_entry.configure(state="normal")
                self.send_button.configure(state="normal")
                self.mic_button.configure(state="normal")
                self.status_label.configure(text="VANGUARD CORE: ACTIVE", text_color="#33FF33")
                self.console_print("SECURE DIALOG OPENED. STANDING BY FOR COMMANDS.", prefix="[VANGUARD] >> ")
                
                # Fetch recent DB history
                history = self.db.get_recent_history(limit=5)
                if history:
                    self.console_print("--- RESUMED RECENT LOGS ---", prefix="")
                    for msg in history:
                        pfx = "[YOU] >> " if msg["role"] == "user" else "[VANGUARD] >> "
                        self.console_print(msg["message"], prefix=pfx)
                    self.console_print("---------------------------", prefix="")

        self.scanner.start()
        play_sound_async("assets/sounds/boot.wav")
        step_loader(0)

    # Animations: Shutdown sequence
    def trigger_shutdown(self) -> None:
        """Triggered upon program closure, plays clean shutdown animation before exit."""
        if self.is_shutting_down:
            return
        
        self.is_shutting_down = True
        play_sound_async("assets/sounds/shutdown.wav")
        self.scanner.set_mode("off")
        self.scanner.stop()
        self.input_entry.configure(state="disabled")
        self.send_button.configure(state="disabled")
        self.mic_button.configure(state="disabled")
        self.status_label.configure(text="VANGUARD CORE: TERMINATING", text_color="#FF3333")
        self.draw_voice_indicator("yellow")
        
        self.console_print("SHUTDOWN COMMAND REGISTERED. CLOSING SECURE LINK...", prefix="[SYSTEM] >> ")
        
        # Shutdown steps
        self.after(400, lambda: self.console_print("CLEANING MEMORY STACKS... OK"))
        self.after(800, lambda: self.console_print("PERSISTING SESSION ARCHIVE... OK"))
        self.after(1200, lambda: self.console_print("DEACTIVATING AI SYNAPSE ROUTERS... OK"))
        self.after(1500, lambda: self.console_print("SYSTEM OFFLINE. GOODBYE."))
        
        def finalize_destroy():
            if self.on_shutdown:
                self.on_shutdown()
            self.destroy()
            
        self.after(2000, finalize_destroy)

    # Actions & Callbacks
    def send_message(self) -> None:
        """Extracts command input, saves to db, clears interface, invokes worker."""
        if not self.boot_complete or self.is_shutting_down:
            return
            
        msg = self.input_entry.get().strip()
        if not msg:
            return
            
        self.input_entry.delete(0, tk.END)
        self.console_print(msg, prefix="[YOU] >> ")
        self.db.add_message("user", msg)
        
        if self.on_send:
            self.on_send(msg)

    def toggle_mic(self) -> None:
        """Toggles microphone status visual indicators."""
        if not self.boot_complete or self.is_shutting_down:
            return
            
        if self.on_mic:
            self.on_mic()

    def set_listening_state(self, is_listening: bool) -> None:
        """Modifies listening state and updates UI colors/labels."""
        self.is_listening = is_listening
        if is_listening:
            play_sound_async("assets/sounds/wake.wav")
            self.draw_voice_indicator("red")
            self.status_label.configure(text="VANGUARD CORE: LISTENING...", text_color="#FF3333")
            self.mic_button.configure(text="🛑 STOP", fg_color="#440000")
            self.scanner.set_mode("talk")
            self.scanner.set_talk_amplitude(0.7)
        else:
            self.draw_voice_indicator("gray")
            self.status_label.configure(text="VANGUARD CORE: ACTIVE", text_color="#33FF33")
            self.mic_button.configure(text="🎤 LISTEN", fg_color="#220000")
            self.scanner.set_mode("scan")

    def set_thinking_state(self, is_thinking: bool) -> None:
        """Modifies AI thinking animation state."""
        self.is_thinking = is_thinking
        if is_thinking:
            self.draw_voice_indicator("yellow")
            self.status_label.configure(text="VANGUARD CORE: PROCESSING...", text_color="#FFFF33")
            self.animate_thinking_label(0)
            self.scanner.set_mode("think")
        else:
            self.draw_voice_indicator("gray")
            self.status_label.configure(text="VANGUARD CORE: ACTIVE", text_color="#33FF33")
            self.thinking_label.configure(text="")
            if not self.is_listening:
                self.scanner.set_mode("scan")

    def animate_thinking_label(self, step: int) -> None:
        """Animates dot cycle while thinking."""
        if not self.is_thinking:
            return
        dots = "." * (step % 4)
        self.thinking_label.configure(text=f"Thinking{dots}")
        self.after(400, lambda: self.animate_thinking_label(step + 1))

    # Fullscreen toggles
    def toggle_fullscreen(self, event=None) -> None:
        """Switches window to full screen."""
        self.attributes("-fullscreen", True)

    def exit_fullscreen(self, event=None) -> None:
        """Restores window from full screen."""
        self.attributes("-fullscreen", False)


# Helper math function for radar scan sine wave animation
def math_sine(x: int, index: int, width: int, height: int) -> float:
    """Computes a composite sine wave coordinate."""
    import math
    if width <= 0:
        return height / 2
    # Sine sweeps
    cycle1 = math.sin((x / width * 4 * math.pi) + (index * 0.1)) * (height * 0.25)
    cycle2 = math.cos((x / width * 2 * math.pi) - (index * 0.05)) * (height * 0.15)
    return (height / 2) + cycle1 + cycle2
