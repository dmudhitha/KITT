# VANGUARD: Futuristic AI Desktop Assistant

VANGUARD (Vehicle Autonomous Network & General Utility Assistant for Research and Diagnostics) is a production-quality, highly modular, and futuristic desktop assistant inspired by the concept of an intelligent talking vehicle.

## Key Features
* **Modular Plugin Architecture**: Dynamically load new commands and functionalities.
* **SQLite Persistent Database**: Full session memory and command execution tracking.
* **Responsive Multi-Threaded Engine**: UI remains responsive using background threads for CPU-intensive tasks like TTS/STT and diagnostics.
* **Futuristic LED Scanner (CustomTkinter)**: Retro scanline animations.

---

## Directory Structure
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
├── assets/                  # Fonts, icons, static assets
├── plugins/                 # Extensible script plugins
├── main.py                  # Orchestrator and application entry point
├── config.py                # Configuration management and overrides
├── database.py              # SQLite memory storage controller
├── utils.py                 # Custom logging and support helpers
└── requirements.txt         # Package dependencies
```

---

## Installation & Setup

1. **Clone or copy this directory** to your desired workspace path.
2. **Install requirements** using pip:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure API settings** by editing `config/settings.json` or by setting the `OPENAI_API_KEY` environment variable.

---

## Verification & Testing (Phase 1)

VANGUARD features a self-test diagnostic tool to verify all database, logging, and configuration sub-systems are operating as intended. 

To run the self-test:
```bash
python3 main.py --dry-run
```
This check ensures:
* The JSON settings configuration is correctly loaded (and environment variables applied).
* The logging directory and rotating log files are set up properly.
* The SQLite tables are created, and database write/read queries execute without issue.
