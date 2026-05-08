# Voice Input

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Platform-Ubuntu](https://img.shields.io/badge/Platform-Ubuntu-orange.svg)](https://ubuntu.com/)
[![Tested_on-Ubuntu_24.04](https://img.shields.io/badge/Tested_on-Ubuntu_24.04-24.04-orange.svg)](https://ubuntu.com/)

[English](README.md) | [中文](README_zh.md) | [한국어](README_ko.md)

---

Voice Input is a global hotkey-based voice dictation tool for Linux. Simply press `Ctrl+Q` to start recording your voice, and the system will automatically transcribe it into text and paste it into your currently focused input field. It supports multiple languages including Chinese, English, Japanese, Korean, and Cantonese, with the best recognition accuracy for Chinese. The UI language adapts to your speaking habits over time. Works seamlessly on both X11 and Wayland desktop sessions, with automatic startup support on system boot.

## Features

- **Global Hotkey** - Press `Alt+Q` to start/stop recording (customizable)
- **Multi-language Support** - Automatic recognition of Chinese, English, Japanese, Korean, Cantonese
- **Smart UI Language** - UI automatically switches to match your speaking habits
- **Dual Platform** - Perfect support for both X11 and Wayland sessions
- **Real-time Volume Display** - Shows volume waveform animation during recording
- **Auto-paste** - Automatically pastes recognized text to focused window
- **Auto-start** - Automatically starts on system boot
- **Offline** - No network required, all processing done locally

## System Requirements

- **Operating System**: Ubuntu 24.04 LTS (tested)
  - Other Ubuntu versions may work but are not officially tested
  - **Not tested on macOS or Windows** - functionality is not guaranteed
- **Desktop Environment**: GNOME (for autostart support)
- **Session Type**: X11 or Wayland
- **Hardware**: Microphone required for voice input
- **Python**: 3.8 or higher

### Required Dependencies

This program requires the following tools:

| Tool | Purpose | Install Command |
|------|---------|----------------|
| xdotool | Window focus detection, keyboard simulation | `sudo apt install xdotool` |
| xsel | Clipboard operations | `sudo apt install xsel` |
| xprop | Window class detection | `sudo apt install x11-utils` |

For Wayland additionally:
| Tool | Purpose | Install Command |
|------|---------|----------------|
| ydotoold | Keyboard simulation on Wayland | `sudo apt install ydotool` |
| wl-copy | Clipboard on Wayland | `sudo apt install wl-clipboard` |

### Window Compatibility

The program automatically detects window types and uses the appropriate paste method:

**Terminal Windows** (use `Ctrl+Shift+V` to paste):
- GNOME Terminal
- Konsole
- xterm, uxterm
- Terminator
- Alacritty
- Kitty
- Tilix
- Terminology
- LilyTerm
- Termite

**GUI Applications** (use `Ctrl+V` to paste):
- All graphical applications (gedit, VS Code, Chrome, Firefox, etc.)
- Electron apps
- Qt applications
- GTK applications

This automatic detection ensures voice input works correctly in both terminal and graphical environments.

## Quick Start

### Installation

```bash
git clone https://github.com/chelkim/voice-input.git ~/.voice-input
cd ~/.voice-input
./setup.sh
```

### Usage

1. Ensure the daemon is running (starts automatically on boot)
2. Click on the target input field
3. Press `Alt+Q` to start recording
4. Speak
5. Press `Alt+Q` again to stop recording
6. Text is automatically pasted into the input field

## Configuration

Configuration file: `~/.config/voice-input/config`

```ini
[hotkey]
# Modifiers + main key. Modifiers: ctrl, alt, shift, meta
key = Alt+Q

[recognition]
# Language: auto (auto-detect), zh (Chinese), en (English), ja (Japanese), ko (Korean), yue (Cantonese)
# Note: Chinese has the best recognition accuracy. Other languages may have lower accuracy.
language = auto

[ui]
# UI display language: auto (auto-detect based on usage), zh, en, ja, ko, yue
# When set to auto, the system learns your preferred language and switches UI accordingly
language = auto
```

**Note about language recognition accuracy:**

The SenseVoice model supports 6 languages, but recognition accuracy varies:
- **Chinese (zh)** - Best accuracy, most training data
- **English (en)** - Good accuracy
- **Japanese (ja), Korean (ko), Cantonese (yue)** - Lower accuracy, may occasionally be confused with Chinese

It is recommended to keep `language = auto` for best results. If you mainly speak Chinese, the model will automatically prioritize Chinese recognition.

**Smart UI language feature:**
- When `[ui] language = auto`, the system automatically detects your speaking patterns
- After 2 consecutive transcriptions in the same language, UI language updates automatically
- For example: if you speak Chinese twice, UI switches to Chinese display
- Language statistics are saved persistently and survive daemon restarts

Restart the service after modifying the config.

## Common Commands

```bash
# Restart service
pkill -f daemon.py && sleep 1 && ~/.voice-input/venv-voice/bin/python3 ~/.voice-input/src/daemon.py &

# Check service status
pgrep -f daemon.py

# View logs
tail -f ~/.voice-input/voice.log
```

## Development

### Project Structure

```
voice-input/
├── src/
│   ├── daemon.py           # Main entry point
│   ├── config.py           # Configuration management
│   ├── platform/           # Platform abstraction layer
│   ├── keyboard/          # Keyboard capture
│   ├── audio/             # Audio recording
│   ├── recognition/       # Speech recognition
│   └── ui/                # User interface
├── tests/                  # Tests
├── scripts/                # Setup scripts
├── README.md               # English version
├── README_zh.md           # Chinese version
├── README_ko.md           # Korean version
├── CONTRIBUTING.md
└── LICENSE
```

### Run Tests

```bash
./venv-voice/bin/python3 tests/test_config.py
```

## Wayland Setup

Wayland requires additional setup:

```bash
# Install ydotoold
sudo apt-get install ydotoold

# Set /dev/uinput permissions
sudo chmod 666 /dev/uinput

# Start ydotoold
ydotoold &
```

## Troubleshooting

### Daemon not responding

```bash
pgrep -f daemon.py  # Check if running
~/.voice-input/venv-voice/bin/python3 ~/.voice-input/src/daemon.py &  # Start manually
```

### ydotool not working on Wayland

1. Ensure ydotoold is running: `ps aux | grep ydotoold`
2. Check /dev/uinput permissions: `ls -la /dev/uinput`

### Cannot paste to terminal

Terminal uses `Ctrl+Shift+V` to paste

This program automatically detects if the target window is a terminal and uses the appropriate paste shortcut (`Ctrl+Shift+V` for terminals, `Ctrl+V` for GUI applications).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT License - see [LICENSE](LICENSE) file.
