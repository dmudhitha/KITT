#!/usr/bin/env bash
# VANGUARD Automated System Installer & Desktop Launcher Setup

echo "==================================================================="
echo "        VANGUARD AI DESKTOP ASSISTANT - SYSTEM INSTALLER"
echo "==================================================================="

# 1. Install System Dependencies (Linux Ubuntu/Debian)
if command -v apt-get &> /dev/null; then
    echo "[+] Installing Linux system audio, TTS, and screenshot dependencies..."
    sudo apt-get update -qq
    sudo apt-get install -y -qq python3-pyaudio espeak-ng scrot xclip
fi

# 2. Install Python Package Requirements
echo "[+] Installing Python package requirements..."
pip install -r requirements.txt --quiet

# 3. Setup Desktop Autostart & Launcher
echo "[+] Registering VANGUARD desktop autostart entry..."
python3 -c "from utils import setup_autostart; setup_autostart(True)"

echo ""
echo "==================================================================="
echo "   INSTALLATION COMPLETE! Run 'python3 main.py' to launch VANGUARD."
echo "==================================================================="
