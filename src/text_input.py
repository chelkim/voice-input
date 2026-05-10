#!/usr/bin/env python3
"""
Typing module - handles text input via clipboard + paste.
"""
import subprocess
import time


def is_terminal_window():
    """Check if current window is a terminal"""
    try:
        window_id = subprocess.run(
            ['xdotool', 'getwindowfocus'],
            capture_output=True, text=True, timeout=1
        ).stdout.strip()

        output = subprocess.run(
            ['xprop', '-id', window_id, 'WM_CLASS'],
            capture_output=True, text=True, timeout=1
        ).stdout.strip().lower()

        terminal_names = ['gnome-terminal', 'konsole', 'xterm', 'uxterm',
                         'terminator', 'alacritty', 'kitty',
                         'tilix', 'terminology', 'lilyterm', 'termite',
                         'gnome-terminal-server', 'warp']

        for term in terminal_names:
            if term in output:
                return True
        return False
    except:
        return False


def paste_text():
    """Paste using appropriate shortcut"""
    try:
        if is_terminal_window():
            subprocess.run(
                ['xdotool', 'key', 'ctrl+shift+v'],
                capture_output=True, timeout=1
            )
        else:
            subprocess.run(
                ['xdotool', 'key', 'ctrl+v'],
                capture_output=True, timeout=1
            )
    except:
        pass


def type_text(text, auto_enter=False):
    """Type text via clipboard + paste"""
    try:
        subprocess.run(
            ['xsel', '--input', '--clipboard'],
            input=text.encode('utf-8'),
            capture_output=True
        )
        time.sleep(0.05)
        paste_text()

        if auto_enter:
            time.sleep(0.05)
            subprocess.run(
                ['xdotool', 'key', 'Return'],
                capture_output=True, timeout=1
            )
    except:
        pass
