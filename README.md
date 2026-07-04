# Antigravity Voice Chat Extension

A seamless, hands-free voice chat extension for the Antigravity AI assistant. 

This extension uses a custom Voice Activity Detection (VAD) algorithm with a lookback buffer and automatic window-switching to allow you to talk to Antigravity continuously without needing to push buttons or even have the chat window focused. Antigravity will also automatically reply using your system's Text-to-Speech!

## Features
- **Continuous Turn-Taking**: Automatically detects when you start and stop speaking.
- **Lookback Buffer**: Never chops off the beginning of your sentences.
- **Auto-Window Switching**: Talk to Antigravity while working in Blender, VS Code, or any other app. It will seamlessly inject your transcribed text into Antigravity in the background.
- **Auto-TTS Integration**: Automatically configures Antigravity to speak its responses out loud.
- **Push-to-Talk Fallback**: Press `F9` to toggle a standard `Ctrl+Space` Push-to-Talk mode.

## Installation

1. Clone or download this repository.
2. Run the automated installer:
   ```bash
   python install.py
   ```
   *The installer will automatically install required Python packages and inject the necessary Agent Rule into your Antigravity `AGENTS.md` configuration file.*

## Usage

1. Open a terminal and run the main script:
   ```bash
   python src/voice_chat.py
   ```
2. You can leave the terminal in the background. Whenever you speak, the extension will transcribe your voice and automatically type it into the Antigravity chat window for you.
3. Antigravity will automatically respond using Text-to-Speech!

## Requirements
- Python 3.10+
- Windows OS (relies on `pygetwindow` for window switching)
