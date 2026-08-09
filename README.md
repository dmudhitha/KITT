# 🏎️ VANGUARD: Futuristic AI Desktop Assistant

> **Vehicle Autonomous Network & General Utility Assistant for Research and Diagnostics**

VANGUARD is a production-quality, highly modular, and futuristic desktop assistant inspired by the concept of an intelligent talking vehicle dashboard from classic science fiction. It is designed to run entirely locally (using **Ollama**) or via cloud providers (like **OpenAI**), coordinating sensory data, system diagnostics, voice synthesis, and dynamic scripting plugins.

![VANGUARD Dashboard](assets/images/dashboard.jpg)

---

## 🚀 Key Subsystems

| Subsystem | Technology | Description |
| :--- | :--- | :--- |
| **GUI Dashboard HUD** | `CustomTkinter` | A high-tech black (`#080808`) cockpit theme with responsive gauges, real-time clock, scrollable log console, and telemetry sweeps. |
| **Bilingual Language Switcher** | `CTkSegmentedButton` | Sidebar HUD widget to dynamically toggle between **English (`en-US`)** and **Sinhala (`si-LK`)** voice capture and processing. |
| **LED Scanner Widget** | Native TK Canvas | A 16-segment horizontal scanner featuring exponential trail decay, glowing filament cores, and active animation modes (`scan`, `think`, `talk`, `off`). |
| **Conversational AI** | `OpenAI API` / `Ollama` | Multithreaded streaming client supporting local/remote models with SQLite context memory injections. Understands both Sinhala and English queries. |
| **Speech Recognition** | `speech_recognition` | Background wake-word monitoring (phonetically tuned to match both English `"hey kit"` and Sinhala `"හේ කිට්"` scripts) and single-shot transcription. |
| **Voice Synthesis** | `pyttsx3` / `espeak-ng` | Pitch-tuned speech synthesis. **Automatically auto-switches** between optimized American English (`en-us+m3`) and Sinhala (`inc/si`) voice engines. |
| **Telemetry Diagnostics** | `psutil` | Real-time scraper polling CPU load, RAM capacity, disk space, battery status, core temperatures, and socket link status. |
| **Global Push-To-Talk Hotkey** | `pynput` | System-wide global shortcut (`Ctrl+Space`) to activate voice commands from anywhere, even when minimized. |
| **System Control Plugins** | Local Execution | Executes OS-level directives: desktop screenshots (`take screenshot`), volume (`set volume 50%`), and screen locking (`lock pc`). |
| **Sci-Fi SFX Soundboard** | `pygame.mixer` | Programmatic multi-frequency audio feedback (`boot`, `shutdown`, `wake`, `plugin`, `calc`, `error`, `scan`). |
| **System Autostart Integration** | `.desktop` Generator | Configures Linux startup entries to auto-launch VANGUARD minimized into tray/badge on boot. |
| **Sci-Fi HUD Theme Switcher** | `CTkOptionMenu` | Hot-swaps UI color themes on the fly (`Neon Red`, `Cyberpunk Cyan`, `Matrix Green`, `Orbital Gold`). |
| **Autonomous Security Alerts** | Background Monitor | Polling worker issuing vocal alerts and red scanner warnings on high CPU load/temp, RAM threshold, or critical low battery (<=20%). |
| **Spoken Startup Briefing** | `BriefingPlugin` | Compiles and vocalizes an executive summary of system diagnostics and environmental weather on boot or demand (`"status report"`). |
| **Smart Voice Timers & Reminders** | `RemindersPlugin` | Countdown timer parser with background vocal alarms and chime notifications (`"remind me in 5 minutes to check deployment"`). |
| **Speech Rate & Pitch Controls** | `CTkSlider` | Dynamic HUD sidebar sliders adjusting TTS speech rate (100-250 WPM) and voice pitch (10-90) on the fly. |
| **Audio Spectrum Visualizer** | `AudioSpectrumVisualizer` | 12-bar real-time frequency spectrum equalizer canvas animating dynamically during active speech and scanning. |
| **Webcam AI Vision Inspection** | `VisionPlugin` | Captures webcam camera snapshots and performs visual scene survey reporting (`"scan webcam"`). |
| **AI Personality Profiles** | `CTkOptionMenu` | Hot-swaps system prompts on the fly (`Tactical KITT`, `AEGIS Security`, `Conversational Butler`, `Cyberpunk Synth`). |
| **System Memory & RAM Cleaner** | `MemoryCleanerPlugin` | Purges Python garbage collection and flushes system RAM caches (`"clean memory"` / `"free ram"`). |
| **System Process & App Killer** | `ProcessKillerPlugin` | Safely terminates unresponsive background processes or applications by name (`"kill process chrome"`). |
| **Clipboard AI Assistant** | `ClipboardAIPlugin` | Reads desktop clipboard content and returns concise AI summaries (`"summarize clipboard"`). |
| **Desktop File Finder & Quick Launcher** | `FileFinderPlugin` | Locates target files across workspace directories (`"find file dashboard.jpg"`). |
| **Manual SFX Soundboard Triggers** | `SoundboardPlugin` | Triggers sci-fi audio sound effects on directive (`"play scan sound"` / `"play error sound"`). |
| **Live Web Search & News Headlines** | `WebSearchPlugin` | Parses live DuckDuckGo web search results and news headlines (`"news updates"` / `"search web AI"`). |
| **System Diagnostic Markdown Exporter** | `DiagnosticExporterPlugin` | Exports formatted Markdown system telemetry reports (`"export diagnostic report"`). |
| **Interactive Help & Manual Center** | `VanguardHelpModal` | `F1` keybinding & header button opening formatted user manual and directive guide. |
| **System Backup & Restore Archive** | `SystemBackupPlugin` | Archives configuration settings and SQLite database into zip backup packages (`"backup system"`). |
| **Standalone Installer & Builder** | `build.sh` & `install.sh` | Automated Linux system installer and PyInstaller standalone binary executable compiler. |
| **Plugin Framework** | Dynamically Imported | Reflection-based local registry executing scripting plugins prior to querying the LLM. |

---

## 📁 Directory Structure

```text
KITT/
├── config/
│   └── settings.json        # Main configuration file (JSON)
├── database/
│   └── memory.db            # SQLite persistent database (created automatically)
├── logs/
│   ├── system.log           # System diagnostic and warning log
│   ├── conversations.log    # Transcripts of chat history
│   └── commands.log         # History of system commands run
├── assets/
│   ├── images/
│   │   └── dashboard.jpg    # Dashboard HUD mockup concept image
│   ├── sounds/              # Synthesized sci-fi SFX audio files (.wav)
│   └── screenshots/         # Captured desktop screenshots
├── plugins/                 # Extensible script plugins (dynamically loaded)
│   ├── briefing.py          # Spoken startup and status report plugin
│   ├── browser.py           # Web browser navigation and search plugin
│   ├── calculator.py        # Safe regular-expression math evaluation plugin
│   ├── macros.py            # Automated multi-action voice macro routine plugin
│   ├── reminders.py         # Voice-activated timers and reminder alarm plugin
│   ├── system_control.py    # Master volume, desktop screenshot, and screen lock plugin
│   └── weather.py           # Environmental weather survey reports
├── main.py                  # Orchestrator and application entry point
├── ui.py                    # CustomTkinter dashboard layout and widgets
├── ai.py                    # Conversational AI connector (OpenAI/Ollama)
├── voice.py                 # TTS Voice Synthesis & STT Speech Recognition
├── diagnostics.py           # Telemetry diagnostics monitor scraper
├── commands.py              # Plugin manager and system core triggers
├── scanner.py               # 16-segment horizontal LED scanner widget
├── utils.py                 # Logging helpers, soundboard generators, autostart manager
└── requirements.txt         # Package dependencies
```

---

## 🛠️ Installation & Setup

### 1. Prerequisites (Linux Systems)
Because VANGUARD utilizes local speech recognition and synthesis, your Linux system requires the PyAudio development header and the eSpeak synthesizer library:
```bash
sudo apt-get update
sudo apt-get install -y python3-pyaudio espeak-ng scrot
```

### 2. Python Package Setup
Clone this repository and install the required Python dependencies:
```bash
pip install -r requirements.txt
```

### 3. Connect to Ollama (Local LLM)
Ensure you have Ollama installed and running on your system:
```bash
# 1. Start Ollama (default port 11434)
ollama serve

# 2. Pull model
ollama pull llama3.2
```

---

## ⚙️ Configuration (`config/settings.json`)

VANGUARD's settings can be adjusted at runtime. Thanks to the hot-reloading pipeline, changes are parsed immediately without restarting the application.

```json
  "api": {
    "provider": "local",                 // "local" for Ollama, "openai" for GPT
    "openai_api_key": "",                // OpenAI API key (if provider is openai)
    "local_url": "http://localhost:11434/v1",
    "local_model": "llama3.2:latest"
  },
  "ui": {
    "theme": "dark",
    "active_theme": "Neon Red",          // "Neon Red", "Cyberpunk Cyan", "Matrix Green", "Orbital Gold"
    "accent_color": "#FF3333"
  },
  "voice": {
    "tts_enabled": true,
    "tts_rate": 150,                     // Speech rate WPM (100 - 250)
    "tts_pitch": 45,                     // Voice pitch (10 - 90)
    "tts_variant": "+m3",                // Espeak voice variant (+m3, +klatt)
    "stt_language": "si-LK"              // Default capture language ("en-US" or "si-LK")
  },
  "routines": {
    "work mode": [
      "open browser github.com",
      "volume 50%",
      "briefing"
    ]
  }
```

---

## 🎯 Verification & Testing

### Subsystem Self-Test
Verify all logging directories, SQLite writes, configurations, and AI connections are working as intended by running VANGUARD in dry-run mode:
```bash
python3 main.py --dry-run
```

### Start Application
```bash
python3 main.py
```

### Directives to Try
* **Global Push-To-Talk**: Press **`Ctrl + Space`** anywhere on your operating system to activate voice listening.
* **HUD Theme Change**: Use the **`HUD COLOR THEME`** dropdown in the sidebar to switch between `Neon Red`, `Cyberpunk Cyan`, `Matrix Green`, and `Orbital Gold`.
* **System Control**: Say or type **`"take screenshot"`**, **`"set volume 70%"`**, or **`"lock pc"`**.
* **Smart Reminders**: Say **`"remind me in 5 minutes to check deployment"`**.
* **Voice Macros**: Say **`"work mode"`** to trigger multi-action automated routines.
* **Bilingual Speech**: Toggle between **`English`** and **`Sinhala`** using the sidebar HUD segmented button.

---

## 📝 Extending with Plugins

Creating new plugins for VANGUARD is straightforward. Add a Python file inside `plugins/` that inherits from `BasePlugin` (in `commands.py`):

```python
# plugins/my_plugin.py
from typing import List, Dict, Any
from commands import BasePlugin

class CustomPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "CustomPlugin"

    @property
    def description(self) -> str:
        return "Executes custom user tasks."

    @property
    def commands(self) -> List[str]:
        return ["custom command", "run test"]

    def execute(self, trigger: str, args: str, context: Dict[str, Any]) -> str:
        return "CUSTOM PLUGIN EXECUTED: All systems operational."
```
VANGUARD will automatically scan, import, and register your plugin on startup!
