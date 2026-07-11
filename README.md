# 🏎️ VANGUARD: Futuristic AI Desktop Assistant

> **Vehicle Autonomous Network & General Utility Assistant for Research and Diagnostics**

VANGUARD is a production-quality, highly modular, and futuristic desktop assistant inspired by the concept of an intelligent talking vehicle dashboard from classic science fiction. It is designed to run entirely locally (using **Ollama**) or via cloud providers (like **OpenAI**), coordinating sensory data, system diagnostics, voice synthesis, and dynamic scripting plugins.

![VANGUARD Dashboard](assets/images/dashboard.jpg)

---

## 🚀 Key Subsystems

| Subsystem | Technology | Description |
| :--- | :--- | :--- |
| **GUI Dashboard HUD** | `CustomTkinter` | A high-tech black (`#080808`) cockpit theme with neon red accents, responsive gauges, real-time clock, scrollable log console, and telemetry sweeps. |
| **LED Scanner Widget** | Native TK Canvas | A 16-segment horizontal scanner featuring exponential trail decay, glowing filament cores, and active animation modes (`scan`, `think`, `talk`, `off`). |
| **Conversational AI** | `OpenAI API` / `Ollama` | Multithreaded streaming client supporting local/remote models with SQLite context memory injections. |
| **Speech Recognition** | `speech_recognition` | Background wake-word monitoring (`"hey kit"`) and single-shot microphone transcription workers. |
| **Voice Synthesis** | `pyttsx3` / `espeak-ng` | Thread-safe, pitch-tuned speech synthesis synchronized with the visual LED scanner. |
| **Telemetry diagnostics** | `psutil` | Real-time scraper polling CPU load, RAM capacity, disk space, battery status, core temperatures, and socket link status. |
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

### Interactions to Try
* **Voice Activation**: Say **`"Hey kit, what is your status?"`** or **`"Hey kit, check my RAM"`**.
* **Dashboard controls**: Click **`🎤 LISTEN`** to bypass the wake-word and capture speech commands immediately.
* **Math Plugin**: Type or say **`"calc (25 + 75) * 5"`** (evaluates locally using safe regex parsing).
* **Browser Plugin**: Type or say **`"open browser github.com"`** (opens your default browser).
* **Weather Plugin**: Type or say **`"weather London"`** (prints a simulated environmental telemetry scan).
* **Console commands**: Type **`"help"`** to view all loaded plugins, or **`"shutdown"`** to safely terminate processes.

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
