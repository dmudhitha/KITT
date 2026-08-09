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

THEMES = {
    "Neon Red": {"accent": "#FF3333", "scanner": "#FF0000", "glow": "#FF8888", "border": "#330000"},
    "Cyberpunk Cyan": {"accent": "#00FFFF", "scanner": "#00CCCC", "glow": "#88FFFF", "border": "#003333"},
    "Matrix Green": {"accent": "#33FF33", "scanner": "#00FF00", "glow": "#88FF88", "border": "#003300"},
    "Orbital Gold": {"accent": "#FFCC00", "scanner": "#FFAA00", "glow": "#FFE688", "border": "#332200"}
}

PERSONALITY_PROFILES = {
    "Tactical KITT": (
        "You are VANGUARD (Vehicle Autonomous Network & General Utility Assistant for Research and Diagnostics), "
        "a sophisticated, futuristic onboard AI desktop assistant. Your personality is analytical, intelligent, "
        "highly capable, and slightly dry. Always reply professionally, concisely, and with a futuristic tone."
    ),
    "AEGIS Security": (
        "You are AEGIS, a high-security tactical defense AI system. Your tone is strict, highly analytical, "
        "authoritative, and focused on system security, telemetry monitoring, and diagnostic enforcement."
    ),
    "Conversational Butler": (
        "You are VANGUARD, a polite, refined, and exceptionally attentive digital butler AI. Your tone is warm, "
        "courteous, highly helpful, and articulate."
    ),
    "Cyberpunk Synth": (
        "You are VANGUARD-NEO, a high-tech cyberpunk AI system operating in a neon-lit digital matrix. "
        "Your tone is edgy, ultra-fast, tech-focused, and filled with sci-fi telemetry jargon."
    )
}


class AudioSpectrumVisualizer:
    """12-bar real-time audio spectrum frequency visualizer widget."""

    def __init__(self, canvas: tk.Canvas, accent_color: str = "#FF3333"):
        self.canvas = canvas
        self.accent_color = accent_color
        self.num_bars = 12
        self.phase = 0.0

    def update(self, is_active: bool = True) -> None:
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width <= 1 or height <= 1:
            return

        bar_width = max(2, (width - (self.num_bars + 1) * 3) / self.num_bars)
        self.phase += 0.25

        for i in range(self.num_bars):
            if is_active:
                h_factor = (math_sine(i * 10, self.phase * 20, width, height) / max(1, height))
                h_factor = max(0.15, min(0.95, abs(h_factor) * (0.6 + (i % 4) * 0.15)))
            else:
                h_factor = 0.08

            bar_h = height * h_factor
            x1 = 3 + i * (bar_width + 3)
            y1 = height - bar_h
            x2 = x1 + bar_width
            y2 = height

            self.canvas.create_rectangle(x1, y1, x2, y2, fill=self.accent_color, outline="")


class VanguardHelpModal(ctk.CTkToplevel):
    """Interactive Help Center & User Manual Modal Dialog."""

    def __init__(self, parent_ui):
        super().__init__(parent_ui)
        self.parent_ui = parent_ui
        self.title("VANGUARD USER MANUAL & COMMAND DIRECTIVES")
        self.geometry("780x540")
        self.configure(fg_color="#080808")
        self.attributes("-topmost", True)

        # Header Label
        title_label = ctk.CTkLabel(
            self,
            text="[ VANGUARD SYSTEM USER MANUAL & VOICE DIRECTIVES ]",
            font=(parent_ui.font_family, 15, "bold"),
            text_color=parent_ui.accent_color
        )
        title_label.pack(pady=(15, 10))

        # Scrollable Text View
        text_box = ctk.CTkTextbox(
            self,
            fg_color="#121212",
            text_color="#00FFFF",
            font=(parent_ui.font_family, 11),
            border_color=parent_ui.accent_color,
            border_width=1
        )
        text_box.pack(fill="both", expand=True, padx=15, pady=10)

        manual_content = """===================================================================
                   VANGUARD SYSTEM USER MANUAL
===================================================================

[1] KEYBOARD SHORTCUTS
-------------------------------------------------------------------
  Ctrl + Space  : Global Push-To-Talk Voice Input (System-Wide)
  F1            : Open User Manual & Command Directives
  F11 / Esc     : Toggle Fullscreen / Normal Mode
  Ctrl + M      : Minimize to Desktop Tray Badge Mode

[2] VOICE DIRECTIVES & COMMAND TRIGGERS
-------------------------------------------------------------------
  SYSTEM CONTROL    : "take screenshot", "volume 50%", "mute", "lock pc"
  STARTUP BRIEFING  : "status report", "briefing", "morning report"
  SMART REMINDERS   : "remind me in 5 minutes to check deployment"
  ALARM CLOCK       : "set alarm for 5:00 PM to submit report"
  RAM CLEANER       : "clean memory", "free ram", "clear cache"
  NETWORK RADAR     : "scan network", "scan lan", "port scan"
  WEBCAM VISION     : "scan webcam", "inspect camera", "camera"
  CLIPBOARD AI      : "summarize clipboard", "read clipboard"
  PROCESS KILLER    : "kill process chrome", "close app firefox"
  BENCHMARK TEST    : "run benchmark", "system test"
  FILE FINDER       : "find file dashboard.jpg", "locate file readme"
  LIVE WEB SEARCH   : "news updates", "search web AI breakthroughs"
  REPORT EXPORTER   : "export diagnostic report", "generate report"
  SECURITY VAULT    : "encrypt text secret", "decrypt text cipher"
  SYSTEM BACKUP     : "backup system", "export memory backup"
  SFX SOUNDBOARD    : "play scan sound", "play boot sound"
  HARDWARE SPECS    : "system specs", "uptime", "hardware specs"
  LOG SEARCH        : "search logs error", "search memory weather"
  VOICE MACROS      : "work mode", "night mode"

[3] INTERFACE CONTROLS
-------------------------------------------------------------------
  INTERFACE LANGUAGE: English (en-US) / Sinhala (si-LK)
  HUD COLOR THEME   : Neon Red, Cyberpunk Cyan, Matrix Green, Orbital Gold
  AI PERSONALITY    : Tactical KITT, AEGIS Security, Butler, Cyberpunk Synth
  SPEECH SLIDERS    : Speech Rate (WPM: 100-250) & Voice Pitch (10-90)
==================================================================="""
        text_box.insert("1.0", manual_content)
        text_box.configure(state="disabled")

        close_btn = ctk.CTkButton(
            self,
            text="CLOSE MANUAL",
            command=self.destroy,
            fg_color=parent_ui.accent_color,
            hover_color="#550000",
            font=(parent_ui.font_family, 11, "bold")
        )
        close_btn.pack(pady=10)


class MiniTrayBadge(ctk.CTkToplevel):
    """Floating borderless desktop badge displayed when VANGUARD main window is minimized."""

    def __init__(self, parent_ui):
        super().__init__(parent_ui)
        self.parent_ui = parent_ui
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(fg_color="#080808")
        
        # Position in bottom-right corner area of desktop
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        w, h = 240, 56
        x = max(10, screen_w - w - 30)
        y = max(10, screen_h - h - 70)
        self.geometry(f"{w}x{h}+{x}+{y}")
        
        self.main_frame = ctk.CTkFrame(self, fg_color="#121212", border_color="#FF3333", border_width=1, corner_radius=8)
        self.main_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        self.scanner_bay = ctk.CTkFrame(self.main_frame, fg_color="#030303", border_color="#330000", border_width=1, width=60, height=28)
        self.scanner_bay.pack(side="left", padx=8, pady=8)
        self.scanner_bay.pack_propagate(False)
        
        self.mini_scanner = LedScanner(self.scanner_bay, num_segments=8, bg_color="#030303", border_color="#330000")
        self.mini_scanner.pack(fill="both", expand=True, padx=2, pady=2)
        self.mini_scanner.start()
        
        self.info_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.info_frame.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        
        self.lbl_title = ctk.CTkLabel(self.info_frame, text="[VANGUARD AI]", font=(parent_ui.font_family, 11, "bold"), text_color="#FF3333")
        self.lbl_title.pack(anchor="w")
        
        self.lbl_hint = ctk.CTkLabel(self.info_frame, text="Double-Click to Restore", font=(parent_ui.font_family, 9), text_color="#00FFFF")
        self.lbl_hint.pack(anchor="w")
        
        # Bindings for double-click restore, drag, and right-click context menu
        widgets = [self, self.main_frame, self.scanner_bay, self.info_frame, self.lbl_title, self.lbl_hint]
        for widget in widgets:
            widget.bind("<Double-1>", lambda e: parent_ui.after(0, parent_ui.show_window))
            widget.bind("<Button-1>", self._start_drag)
            widget.bind("<B1-Motion>", self._do_drag)
            widget.bind("<Button-3>", self._show_context_menu)
        
        self._drag_x = 0
        self._drag_y = 0
        
        # Right-click context popup menu
        self.menu = tk.Menu(self, tearoff=0, bg="#121212", fg="#FFFFFF", activebackground="#FF3333", activeforeground="#FFFFFF")
        self.menu.add_command(label="Open VANGUARD", command=lambda: parent_ui.after(0, parent_ui.show_window))
        self.menu.add_command(label="Toggle Mute", command=lambda: parent_ui.after(0, parent_ui.toggle_mute_from_tray))
        self.menu.add_separator()
        self.menu.add_command(label="Exit VANGUARD", command=lambda: parent_ui.after(0, parent_ui.trigger_shutdown))

    def _start_drag(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _do_drag(self, event):
        x = self.winfo_x() + (event.x - self._drag_x)
        y = self.winfo_y() + (event.y - self._drag_y)
        self.geometry(f"+{x}+{y}")

    def _show_context_menu(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def show_badge(self):
        self.deiconify()
        self.lift()


class VanguardUI(ctk.CTk):
    """Futuristic dashboard UI class for VANGUARD assistant."""

    def __init__(
        self,
        config_manager,
        db_manager,
        on_send_callback: Optional[Callable[[str], None]] = None,
        on_mic_callback: Optional[Callable[[], None]] = None,
        on_shutdown_callback: Optional[Callable[[], None]] = None,
        on_speak_callback: Optional[Callable[[str], None]] = None,
    ):
        super().__init__()
        self.config = config_manager
        self.db = db_manager
        self.diagnostics = SystemDiagnostics()
        self.on_send = on_send_callback
        self.on_mic = on_mic_callback
        self.on_shutdown = on_shutdown_callback
        self.on_speak = on_speak_callback

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
        self.tray_icon = None

        # Key & Window Bindings
        self.bind("<F1>", lambda e: self.open_help_modal())
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.exit_fullscreen)
        self.bind("<Unmap>", self._on_unmap)
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
        self.setup_system_tray()

        # Initialize Mini Desktop Tray Badge overlay
        try:
            self.mini_badge = MiniTrayBadge(self)
            self.mini_badge.withdraw()
        except Exception as e:
            logger.warning(f"Could not initialize MiniTrayBadge: {e}")
            self.mini_badge = None

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

        # 3. Clock, Date, and Manual Button
        self.time_date_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.time_date_frame.grid(row=0, column=2, sticky="e", padx=15)

        self.help_btn = ctk.CTkButton(
            self.time_date_frame,
            text="📖 MANUAL (F1)",
            command=self.open_help_modal,
            fg_color="#1A1A1A",
            hover_color="#333333",
            text_color=self.accent_color,
            width=110,
            height=28,
            font=(self.font_family, 10, "bold")
        )
        self.help_btn.pack(side="top", pady=(2, 4))

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

        # Language Switcher Segmented Button
        self.lang_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.lang_frame.pack(fill="x", padx=15, pady=(15, 5))
        
        self.lang_label = ctk.CTkLabel(
            self.lang_frame,
            text="INTERFACE LANGUAGE",
            font=(self.font_family, 11, "bold"),
            text_color=self.accent_color
        )
        self.lang_label.pack(anchor="w", pady=2)
        
        current_lang = self.config.get("voice", "stt_language", "en-US")
        initial_val = "Sinhala" if current_lang == "si-LK" else "English"
        
        self.lang_toggle = ctk.CTkSegmentedButton(
            self.lang_frame,
            values=["English", "Sinhala"],
            command=self.change_language,
            selected_color=self.accent_color,
            selected_hover_color="#550000",
            fg_color="#1A1A1A",
            text_color="#FFFFFF"
        )
        self.lang_toggle.set(initial_val)
        self.lang_toggle.pack(fill="x", pady=2)

        # HUD Theme Selector
        self.theme_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.theme_frame.pack(fill="x", padx=15, pady=(10, 5))
        
        self.theme_label = ctk.CTkLabel(
            self.theme_frame,
            text="HUD COLOR THEME",
            font=(self.font_family, 11, "bold"),
            text_color=self.accent_color
        )
        self.theme_label.pack(anchor="w", pady=2)
        
        active_theme = self.config.get("ui", "active_theme", "Neon Red")
        
        self.theme_menu = ctk.CTkOptionMenu(
            self.theme_frame,
            values=["Neon Red", "Cyberpunk Cyan", "Matrix Green", "Orbital Gold"],
            command=self.change_theme,
            fg_color="#1A1A1A",
            button_color=self.accent_color,
            button_hover_color="#550000",
            text_color="#FFFFFF"
        )
        self.theme_menu.set(active_theme)
        self.theme_menu.pack(fill="x", pady=2)

        # TTS Sliders Frame
        self.tts_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.tts_frame.pack(fill="x", padx=15, pady=(10, 5))

        self.tts_label = ctk.CTkLabel(
            self.tts_frame,
            text="SPEECH RATE & PITCH",
            font=(self.font_family, 11, "bold"),
            text_color=self.accent_color
        )
        self.tts_label.pack(anchor="w", pady=2)

        cur_rate = self.config.get("voice", "tts_rate", 150)
        self.rate_slider = ctk.CTkSlider(
            self.tts_frame,
            from_=100,
            to=250,
            command=self.change_tts_rate,
            button_color=self.accent_color,
            progress_color=self.accent_color
        )
        self.rate_slider.set(cur_rate)
        self.rate_slider.pack(fill="x", pady=2)

        cur_pitch = self.config.get("voice", "tts_pitch", 45)
        self.pitch_slider = ctk.CTkSlider(
            self.tts_frame,
            from_=10,
            to=90,
            command=self.change_tts_pitch,
            button_color=self.accent_color,
            progress_color=self.accent_color
        )
        self.pitch_slider.set(cur_pitch)
        self.pitch_slider.pack(fill="x", pady=2)

        # AI Personality Profile Selector
        self.profile_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.profile_frame.pack(fill="x", padx=15, pady=(10, 5))
        
        self.profile_label = ctk.CTkLabel(
            self.profile_frame,
            text="AI PERSONALITY PROFILE",
            font=(self.font_family, 11, "bold"),
            text_color=self.accent_color
        )
        self.profile_label.pack(anchor="w", pady=2)
        
        active_profile = self.config.get("api", "active_profile", "Tactical KITT")
        
        self.profile_menu = ctk.CTkOptionMenu(
            self.profile_frame,
            values=["Tactical KITT", "AEGIS Security", "Conversational Butler", "Cyberpunk Synth"],
            command=self.change_personality,
            fg_color="#1A1A1A",
            button_color=self.accent_color,
            button_hover_color="#550000",
            text_color="#FFFFFF"
        )
        self.profile_menu.set(active_profile)
        self.profile_menu.pack(fill="x", pady=2)

    def change_personality(self, profile_name: str) -> None:
        """Dynamically hot-reloads AI personality system prompt."""
        if profile_name not in PERSONALITY_PROFILES:
            return
        prompt = PERSONALITY_PROFILES[profile_name]
        self.config.set("api", "active_profile", profile_name)
        self.config.set("api", "system_prompt", prompt)
        
        play_sound_async("assets/sounds/plugin.wav")
        self.console_print(f"AI PERSONALITY PROFILE UPDATED TO '{profile_name.upper()}'.", prefix="[SYSTEM] >> ")

    def change_tts_rate(self, value: float) -> None:
        """Dynamically adjusts speech synthesis rate (WPM)."""
        rate = int(value)
        self.config.set("voice", "tts_rate", rate)

    def change_tts_pitch(self, value: float) -> None:
        """Dynamically adjusts speech synthesis pitch."""
        pitch = int(value)
        self.config.set("voice", "tts_pitch", pitch)

    def change_theme(self, theme_name: str) -> None:
        """Applies theme color scheme instantly across all GUI elements."""
        if theme_name not in THEMES:
            return
        colors = THEMES[theme_name]
        self.accent_color = colors["accent"]
        self.config.set("ui", "active_theme", theme_name)
        self.config.set("ui", "accent_color", colors["accent"])
        
        # Update colors on header, sidebar title, buttons, progress bars
        self.logo_label.configure(text_color=self.accent_color)
        self.sidebar_title.configure(text_color=self.accent_color)
        self.telemetry_title.configure(text_color=self.accent_color)
        self.lang_label.configure(text_color=self.accent_color)
        self.theme_label.configure(text_color=self.accent_color)
        self.theme_menu.configure(button_color=self.accent_color)
        self.lang_toggle.configure(selected_color=self.accent_color)
        self.cpu_bar.configure(progress_color=self.accent_color)
        self.ram_bar.configure(progress_color=self.accent_color)
        self.disk_bar.configure(progress_color=self.accent_color)
        self.send_button.configure(fg_color=self.accent_color)
        self.mic_button.configure(fg_color=self.accent_color)
        self.console_textbox.configure(border_color=self.accent_color)
        
        # Update scanner LED color
        if hasattr(self, "scanner") and self.scanner:
            self.scanner.glow_color = colors["scanner"]

        if hasattr(self, "spectrum") and self.spectrum:
            self.spectrum.accent_color = colors["accent"]
            
        self.rate_slider.configure(button_color=self.accent_color, progress_color=self.accent_color)
        self.pitch_slider.configure(button_color=self.accent_color, progress_color=self.accent_color)
        self.profile_menu.configure(button_color=self.accent_color)
        self.profile_label.configure(text_color=self.accent_color)
        self.tts_label.configure(text_color=self.accent_color)
        if hasattr(self, "help_btn") and self.help_btn:
            self.help_btn.configure(text_color=self.accent_color)

    def open_help_modal(self) -> None:
        """Opens the interactive user manual and command directive modal."""
        try:
            VanguardHelpModal(self)
        except Exception as e:
            logger.error(f"Could not open help modal: {e}")
        
        play_sound_async("assets/sounds/plugin.wav")
        self.console_print(f"HUD THEME CHANGED TO '{theme_name.upper()}'.", prefix="[SYSTEM] >> ")

    def change_language(self, language: str) -> None:
        """Toggles speech-to-text and text-to-speech language preference."""
        if language == "Sinhala":
            self.config.set("voice", "stt_language", "si-LK")
            self.console_print("SPEECH INTERFACE SET TO SINHALA [si-LK]", prefix="[SYSTEM] >> ")
        else:
            self.config.set("voice", "stt_language", "en-US")
            self.console_print("SPEECH INTERFACE SET TO ENGLISH [en-US]", prefix="[SYSTEM] >> ")

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

                # 6. Check Autonomous Security Thresholds
                now = time.time()
                if not hasattr(self, "_last_alert_time"):
                    self._last_alert_time = 0
                    
                if now - self._last_alert_time > 180:  # Cooldown 3 minutes
                    cpu_warn = self.config.get("diagnostics", "cpu_warning_threshold", 80.0)
                    ram_warn = self.config.get("diagnostics", "ram_warning_threshold", 85.0)
                    
                    alert_msg = None
                    if battery.get("present", False) and not battery.get("power_plugged", True) and battery.get("percent", 100) <= 20:
                        alert_msg = f"VANGUARD BATTERY SECURITY ALERT: Critical low battery detected at {battery['percent']}%. Connect AC power supply."
                    elif cpu > cpu_warn:
                        alert_msg = f"VANGUARD SECURITY ALERT: High CPU load detected at {cpu}%."
                    elif ram > ram_warn:
                        alert_msg = f"VANGUARD SECURITY ALERT: High RAM memory utilization detected at {ram}%."
                        
                    if alert_msg:
                        self._last_alert_time = now
                        play_sound_async("assets/sounds/error.wav")
                        self.console_print(alert_msg, prefix="[SECURITY ALERT] >> ")
                        self.speak(alert_msg)
                    
            except Exception as e:
                logger.error(f"Error updating GUI diagnostics: {e}")

        self.after(self.config.get("diagnostics", "poll_interval_ms", 1000), self.update_diagnostics)

        # Audio Spectrum Visualizer Canvas
        self.spectrum_canvas = tk.Canvas(
            self.sidebar,
            bg="#030303",
            highlightthickness=1,
            highlightbackground="#330000",
            height=35
        )
        self.spectrum_canvas.pack(fill="x", padx=15, pady=(2, 5))
        self.spectrum = AudioSpectrumVisualizer(self.spectrum_canvas, accent_color=self.accent_color)

    def animate_telemetry(self) -> None:
        """Renders an animated scanning telemetry sine sweep and audio spectrum visualizer."""
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

        # Update Audio Spectrum Visualizer
        if hasattr(self, "spectrum") and self.spectrum:
            is_active = self.is_listening or self.is_thinking or (hasattr(self, "scanner") and self.scanner and self.scanner.animation_running)
            self.spectrum.update(is_active=is_active)

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

                # Trigger Automatic Startup Briefing if enabled
                if self.config.get("briefing", "enabled", True):
                    self.after(600, self.trigger_boot_briefing)

        self.scanner.start()
        play_sound_async("assets/sounds/boot.wav")
        step_loader(0)

    def trigger_boot_briefing(self) -> None:
        """Compiles and speaks the automatic startup briefing upon boot completion."""
        try:
            from plugins.briefing import BriefingPlugin
            plugin = BriefingPlugin()
            location = self.config.get("briefing", "location", "Colombo")
            text = plugin.generate_briefing(location)
            self.console_print(text, prefix="[SYSTEM BRIEFING] >> ")
            logger.info(f"Automatic Spoken Startup Briefing triggered: {text[:60]}...")
            self.speak(text)
        except Exception as e:
            logger.error(f"Boot briefing failed: {e}")

    def speak(self, text: str) -> None:
        """Delivers text to the background voice synthesizer if available."""
        if self.on_speak:
            self.on_speak(text)

    # System Tray & Window State Management
    def setup_system_tray(self) -> None:
        """Initializes non-blocking System Tray icon with right-click menu and double-click restore actions."""
        try:
            # Enable AyatanaAppIndicator3 alias for modern Linux GNOME desktops
            import gi
            try:
                gi.require_version('AppIndicator3', '0.1')
            except (ValueError, AttributeError):
                try:
                    gi.require_version('AyatanaAppIndicator3', '0.1')
                    from gi.repository import AyatanaAppIndicator3
                    import sys
                    sys.modules['gi.repository.AppIndicator3'] = AyatanaAppIndicator3
                except Exception:
                    pass

            import pystray
            from PIL import Image, ImageDraw

            # Generate high-tech 64x64 icon (dark background with glowing neon red scanner bar)
            img = Image.new('RGB', (64, 64), color='#080808')
            draw = ImageDraw.Draw(img)
            draw.rectangle([4, 4, 59, 59], outline='#FF3333', width=2)
            draw.rectangle([10, 26, 53, 37], fill='#FF0000', outline='#FF8888')
            draw.rectangle([22, 28, 41, 35], fill='#FFFFFF')

            # Define context menu options
            # Setting default=True on 'Open VANGUARD' enables double-click restore behavior
            menu = pystray.Menu(
                pystray.MenuItem("Open VANGUARD", lambda icon, item: self.after(0, self.show_window), default=True),
                pystray.MenuItem("Toggle Mute", lambda icon, item: self.after(0, self.toggle_mute_from_tray)),
                pystray.MenuItem("Exit VANGUARD", lambda icon, item: self.after(0, self.trigger_shutdown))
            )

            self.tray_icon = pystray.Icon("VANGUARD", img, "VANGUARD AI Assistant", menu)
            self.tray_icon.run_detached()
            logger.info("System Tray interface active (Double-click or Right-click -> Open to restore).")
        except Exception as e:
            logger.warning(f"Could not initialize System Tray icon: {e}")
            self.tray_icon = None

    def show_window(self) -> None:
        """Restores and displays the application window from system tray or mini badge."""
        if self.is_shutting_down:
            return
        if hasattr(self, "mini_badge") and self.mini_badge:
            try:
                self.mini_badge.withdraw()
            except Exception:
                pass
        self.deiconify()
        self.state("normal")
        self.lift()
        self.focus_force()
        self.console_print("WINDOW RESTORED TO SCREEN.", prefix="[SYSTEM] >> ")

    def _on_unmap(self, event) -> None:
        """Intercepts window minimize action to hide main window cleanly from OS taskbar and present mini desktop tray badge."""
        if event.widget == self and not self.is_shutting_down:
            # Schedule delayed withdraw to ensure window manager completes unmap transition
            self.after(10, self._do_withdraw_to_tray)

    def _do_withdraw_to_tray(self) -> None:
        """Executes actual withdraw to remove window from OS taskbar and show tray badge."""
        if self.is_shutting_down:
            return
        if self.state() == "iconic":
            self.withdraw()
            if hasattr(self, "mini_badge") and self.mini_badge:
                try:
                    self.mini_badge.show_badge()
                except Exception:
                    pass
            self.console_print("WINDOW MINIMIZED & REMOVED FROM TASKBAR. FLOATING TRAY BADGE ACTIVE.", prefix="[SYSTEM] >> ")

    def toggle_mute_from_tray(self) -> None:
        """Toggles mute mode from tray icon menu."""
        current_mute = self.config.get("voice", "mute_mode", False)
        new_mute = not current_mute
        self.config.set("voice", "mute_mode", new_mute)
        status_text = "MUTED" if new_mute else "UNMUTED"
        self.console_print(f"VOICE SYNTHESIS {status_text} VIA TRAY CONTROLS.", prefix="[SYSTEM] >> ")

    # Animations: Shutdown sequence
    def trigger_shutdown(self) -> None:
        """Triggered upon program closure, plays clean shutdown animation before exit."""
        if self.is_shutting_down:
            return
        
        self.is_shutting_down = True
        if hasattr(self, "mini_badge") and self.mini_badge:
            try:
                self.mini_badge.destroy()
                self.mini_badge = None
            except Exception:
                pass

        if self.tray_icon:
            try:
                self.tray_icon.stop()
                self.tray_icon = None
            except Exception as e:
                logger.debug(f"Error stopping system tray icon: {e}")

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
