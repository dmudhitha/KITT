# 🏎️ VANGUARD: Futuristic AI Desktop Assistant

> **Vehicle Autonomous Network & General Utility Assistant for Research and Diagnostics**

VANGUARD is a production-quality, highly modular, and futuristic desktop assistant inspired by the concept of an intelligent talking vehicle dashboard from classic science fiction. It is designed to run entirely locally (using **Ollama**) or via cloud providers (like **OpenAI**), coordinating sensory data, system diagnostics, voice synthesis, and dynamic scripting plugins.

![VANGUARD Dashboard](assets/images/dashboard.jpg)

---

## 🚀 Key Subsystems

| Subsystem | Technology | Description |
| :--- | :--- | :--- |
| **GUI Dashboard HUD** | `CustomTkinter` | A high-tech black (`#080808`) cockpit theme with neon red accents, responsive gauges, real-time clock, scrollable log console, and telemetry sweeps. |
| **Bilingual Language Switcher** | `CTkSegmentedButton` | A dedicated UI toggle widget in the sidebar to switch between **English** and **Sinhala** voice inputs on the fly, instantly hot-reloading configurations. |
| **LED Scanner Widget** | Native TK Canvas | A 16-segment horizontal scanner featuring exponential trail decay, glowing filament cores, and active animation modes (`scan`, `think`, `talk`, `off`). |
| **Conversational AI** | `OpenAI API` / `Ollama` | Multithreaded streaming client supporting local/remote models with SQLite context memory injections. Understands both Sinhala and English queries. |
| **Speech Recognition** | `speech_recognition` | Background wake-word monitoring (phonetically tuned to match both English `"hey kit"` and Sinhala `"හේ කිට්"` scripts) and single-shot transcription. |
| **Voice Synthesis** | `pyttsx3` / `espeak-ng` | Pitch-tuned speech synthesis. **Automatically auto-switches** between optimized American English (`en-us+m3`) and Sinhala (`inc/si`) voice engines by scanning Unicode character blocks. |
| **Telemetry Diagnostics** | `psutil` | Real-time scraper polling CPU load, RAM capacity, disk space, battery status, core temperatures, and socket link status. |
| **Global Push-To-Talk Hotkey** | `pynput` | System-wide global shortcut (`Ctrl+Space`) to activate voice commands from anywhere, even when minimized. |
| **System Control Plugins** | Local Execution | Executes OS-level directives: desktop screenshots (`take screenshot`), volume (`set volume 50%`), and screen locking (`lock pc`). |
| **Sci-Fi SFX Soundboard** | `pygame.mixer` | Programmatic multi-frequency audio feedback (`boot`, `shutdown`, `wake`, `plugin`, `calc`, `error`, `scan`). |
| **System Autostart Integration** | `.desktop` Generator | Configures Linux startup entries to auto-launch VANGUARD minimized into tray/badge on boot. |
| **Sci-Fi HUD Theme Switcher** | `CTkOptionMenu` | Hot-swaps UI color themes on the fly (`Neon Red`, `Cyberpunk Cyan`, `Matrix Green`, `Orbital Gold`). |
| **Autonomous Security Alerts** | Background Monitor | Polling worker issuing vocal alerts and red scanner warnings on high CPU load/temp or RAM threshold breaches. |
| **Smart Voice Timers & Reminders** | `RemindersPlugin` | Countdown timer parser with background vocal alarms and chime notifications (`"remind me in 5 minutes"`). |
| **Speech Rate & Pitch Controls** | `CTkSlider` | Dynamic HUD sidebar sliders adjusting TTS speech rate (100-250 WPM) and voice pitch (10-90) on the fly. |
| **Audio Spectrum Visualizer** | `AudioSpectrumVisualizer` | 12-bar real-time frequency spectrum equalizer canvas animating dynamically during active speech. |
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
│   └── images/
│       └── dashboard.jpg    # Dashboard HUD mockup concept image
├── plugins/                 # Extensible script plugins (dynamically loaded)
│   ├── browser.py           # Web browser navigation and search plugin
│   ├── calculator.py        # Safe regular-expression math evaluation plugin
│   └── weather.py           # Simulated environment survey reports
├── main.py                  # Orchestrator and application entry point
├── ui.py                    # CustomTkinter dashboard layout and widgets
├── ai.py                    # Conversational AI connector (OpenAI/Ollama)
├── voice.py                 # TTS Voice Synthesis & STT Speech Recognition
├── diagnostics.py           # Telemetry diagnostics monitor scraper
├── commands.py              # Plugin manager and system core triggers
├── utils.py                 # Custom logging and audio generators
└── requirements.txt         # Package dependencies
```

---

## 🛠️ Installation & Setup

### 1. Prerequisites (Linux Systems)
Because VANGUARD utilizes local speech recognition and synthesis, your Linux system requires the PyAudio development header and the eSpeak synthesizer library. Run:
```bash
sudo apt-get update
sudo apt-get install -y python3-pyaudio espeak-ng
```

### 2. Python Package Setup
Clone this directory and install the required Python packages:
```bash
pip install -r requirements.txt
```

### 3. Connect to Ollama (Local LLM)
Ensure you have Ollama installed and running on your system:
```bash
# 1. Start Ollama (usually runs on port 11434)
ollama serve

# 2. Pull the default model
ollama pull llama3.2
```
VANGUARD's `config/settings.json` is pre-configured to look for your local Ollama setup using `llama3.2:latest`. If you wish to use a different model, simply update the `"local_model"` parameter in the JSON configuration.

---

## ⚙️ Configuration (`config/settings.json`)

VANGUARD's settings can be adjusted at runtime. Thanks to the hot-reloading pipeline, any change made to the config file is parsed immediately without restarting the application.

```json
  "api": {
    "provider": "local",                 // "local" for Ollama, "openai" for GPT
    "openai_api_key": "",                // OpenAI API key (if provider is openai)
    "local_url": "http://localhost:11434/v1",
    "local_model": "llama3.2:latest",    // Target Ollama model name
    "system_prompt": "..."
  },
  "voice": {
    "tts_enabled": true,
    "tts_rate": 150,                     // Clear speech rate (words per minute)
    "tts_volume": 1.0,
    "tts_pitch": 45,                     // Futuristic deeper pitch
    "tts_variant": "+m3",                // Espeak voice variant (e.g. +m3, +klatt)
    "stt_language": "si-LK",             // Default capture language ("en-US" or "si-LK")
    "wake_word": "hey kitt"
  }
```

> [!NOTE]
> Setting `"tts_pitch"` to `45` and `"tts_variant"` to `"+m3"` gives VANGUARD a deeper, warmer, and much more natural-sounding voice compared to standard robotic espeak text-to-speech.

---

## 🎯 Verification & Testing

### Subsystem Self-Test
Verify all logging directories, SQLite writes, configurations, and AI connections are working as intended by running VANGUARD in dry-run mode:
```bash
python3 main.py --dry-run
```

### Run the Application
Start the graphical dashboard:
```bash
python3 main.py
```

### Bilingual Interactions to Try
* **Switching Languages**: Locate the **INTERFACE LANGUAGE** toggle at the bottom-left of the sidebar HUD. Click **`Sinhala`** or **`English`** to swap modes instantly.
* **Sinhala Activation**: With the toggle set to `Sinhala`, say **`"හේ කිට්"`** or **`"කිට්"`** (or click **`🎤 LISTEN`**). Ask: **`"ඔයාගේ තත්ත්වය මොකක්ද?"`** (What is your status?).
* **English Activation**: Toggle back to `English` and say **`"Hey kit, check my RAM"`**.
* **Auto-Voice Switching**: If the response is generated in Sinhala script, the speaker will load the native Sinhala voice engine (`inc/si`). If the response is in English, it will use the optimized American English engine (`en-us+m3`).

---

## 📝 Extending with Plugins
Adding new capabilities to VANGUARD is simple. Create a python file inside `plugins/` that inherits from `BasePlugin` (found in `commands.py`) and implement a `handle(self, command: str, context: dict) -> str` method:

```python
# plugins/my_plugin.py
from commands import BasePlugin

class MyPlugin(BasePlugin):
    def get_triggers(self) -> list:
        return ["hello", "greet"]

    def handle(self, command: str, context: dict) -> str:
        return "Greetings, Creator. All secondary matrices are functioning normally."
```
VANGUARD will automatically scan, import, and register your new plugin triggers on startup!
