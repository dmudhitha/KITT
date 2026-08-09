#!/usr/bin/env bash
# VANGUARD PyInstaller Standalone Build Script

echo "==================================================================="
echo "     VANGUARD STANDALONE BINARY BUILDER (PyInstaller)"
echo "==================================================================="

# 1. Install PyInstaller if not present
python3 -m pip install --quiet pyinstaller

# 2. Clean previous build artifacts
rm -rf build dist

# 3. Execute PyInstaller compilation
pyinstaller \
  --noconfirm \
  --onedir \
  --windowed \
  --name "VANGUARD" \
  --add-data "config:config" \
  --add-data "assets:assets" \
  --add-data "plugins:plugins" \
  --hidden-import "PIL" \
  --hidden-import "pystray" \
  --hidden-import "pygame" \
  --hidden-import "pynput" \
  --hidden-import "psutil" \
  --hidden-import "customtkinter" \
  main.py

echo ""
echo "==================================================================="
echo "   BUILD COMPLETE! Binary package created at: ./dist/VANGUARD/VANGUARD"
echo "==================================================================="
