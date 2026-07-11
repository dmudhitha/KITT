# Knight Rider KITT AI Assistant - Python Project Prompt

## Project Overview

Create a complete Python application that simulates a futuristic AI assistant inspired by the iconic Knight Rider KITT vehicle. The application should feature an immersive dashboard interface, voice interaction, intelligent conversation, and modular architecture while remaining an original implementation without copying copyrighted assets.

---

# Technical Requirements

## Core Technologies

* Python 3.12+
* CustomTkinter (preferred) or PyQt6
* Object-Oriented Programming (OOP)
* Modular architecture
* Threading or asyncio for responsiveness

---

# User Interface

Design a futuristic dashboard with:

* Black background
* Red neon accents
* Glowing UI elements
* Animated Knight Rider-style LED scanner
* Digital clock
* System status panel
* Conversation window
* Voice activity indicator
* "Thinking..." animation
* Startup animation
* Shutdown animation
* Smooth transitions
* Responsive layout
* Full-screen dashboard mode
* HUD-style interface
* Radar animation (bonus)

---

# AI Features

Implement:

* Conversation with an LLM (OpenAI API or configurable alternative)
* Session memory
* Configurable API provider
* Streaming responses (preferred)
* Typing animation
* Conversation history
* Graceful API error handling
* SQLite conversation memory (bonus)
* Local LLM support (Ollama / LM Studio)

---

# Voice Features

Support:

* SpeechRecognition
* pyttsx3 Text-to-Speech
* Deep male voice if available
* Keyboard input
* Microphone input
* Wake word ("Hey KITT") (bonus)
* Mute mode
* Wake mode

---

# Dashboard Features

Display real-time:

* CPU usage
* RAM usage
* Disk usage
* Battery level
* Network status
* System temperature (if available)
* Current time
* Date

Use `psutil` where applicable.

---

# Commands

Implement built-in commands:

* System status
* Open browser
* Open calculator
* Shutdown assistant
* Restart assistant
* Mute
* Wake up
* Help
* Time
* Date

Design a plugin system so additional commands can be added easily.

---

# Configuration

Store settings in JSON.

Include:

* API key
* Voice settings
* Theme settings
* Window settings
* Wake word settings
* Logging options

---

# Logging

Create logs for:

* Conversations
* Errors
* Commands
* System events

---

# Project Structure

```text
KITT-AI/
│
├── main.py
├── config.py
├── ui.py
├── ai.py
├── voice.py
├── commands.py
├── diagnostics.py
├── scanner.py
├── utils.py
├── database.py
│
├── plugins/
│   ├── weather.py
│   ├── browser.py
│   ├── calculator.py
│   └── ...
│
├── assets/
│   ├── sounds/
│   ├── icons/
│   ├── fonts/
│   └── images/
│
├── logs/
│
├── config/
│   └── settings.json
│
├── database/
│   └── memory.db
│
├── requirements.txt
└── README.md
```

---

# Code Quality Requirements

Generate production-quality code.

Requirements:

* Type hints
* Docstrings
* Modular design
* OOP principles
* Clear comments
* Error handling
* Logging
* Clean architecture
* PEP 8 compliance

---

# Required Python Libraries

```text
customtkinter
pyttsx3
SpeechRecognition
pyaudio
psutil
requests
openai
pillow
pygame
python-dotenv
sqlite3
asyncio
threading
```

---

# Bonus Features

Implement as many as possible:

* Wake word detection
* Face recognition
* Camera support
* Weather
* Music player
* Spotify integration
* Internet search
* Maps
* Home automation
* Vehicle telemetry simulation
* Animated radar
* Voice visualization
* Ambient sounds
* Multiple personalities
* Plugin marketplace architecture
* Auto updates
* Theme switching
* OLED dashboard mode
* Offline mode using Ollama
* Voice authentication
* Gesture control
* Smart reminders
* Calendar integration
* Email assistant

---

# Design Goals

The interface should feel like a premium futuristic AI vehicle dashboard.

Focus on:

* Smooth animations
* Neon glow effects
* Responsive controls
* Modern HUD design
* Elegant transitions
* Minimal latency
* High frame-rate animations
* Professional appearance

---

# Deliverables

Generate:

1. Complete source code.
2. All project files.
3. `requirements.txt`
4. `README.md`
5. Configuration files.
6. Example plugins.
7. Installation guide.
8. API setup instructions.
9. Well-documented code.
10. A fully functional application that is easy to extend.

---

# Final Objective

Create a polished, modular, extensible AI assistant that delivers an immersive experience inspired by the concept of an intelligent futuristic vehicle. The application should combine conversational AI, voice interaction, real-time system monitoring, animated dashboard visuals, and plugin-based extensibility into a responsive desktop application suitable for further expansion.
