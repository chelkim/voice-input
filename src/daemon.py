#!/usr/bin/env python3
"""
Voice Input Daemon - Global hotkey voice input tool.
"""

import os
import sys
import time
import signal
import threading
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR.parent))

from src.config import HOTKEY_CONFIG, detect_language_from_text, record_transcription_language
from src.sysplatform import PlatformTools
from src.audio import AudioRecorder
from src.recognition import SenseVoiceRecognizer
from src.ipc_manager import IPCManager
from src.keyboard.x11 import X11KeyboardCapture
from src.keyboard.wayland import WaylandKeyboardCapture

LOG_FILE = "/tmp/voice-log.txt"

def get_session_type() -> str:
    session = os.environ.get('XDG_SESSION_TYPE', '').lower()
    if session in ('wayland', 'x11'):
        return session
    if os.environ.get('WAYLAND_DISPLAY'):
        return 'wayland'
    if os.environ.get('DISPLAY'):
        return 'x11'
    return 'unknown'

def get_timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S.%%03d") % (time.time() % 1 * 1000)

def log(msg):
    ts = get_timestamp()
    print(f"[{ts}] {msg}", flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{ts}] {msg}\n")

SESSION_TYPE = get_session_type()
print(f"Detected session type: {SESSION_TYPE}")

ipc = IPCManager()
platform = None
keyboard_capture = None
audio_recorder = AudioRecorder()
recognizer = None
target_window = None


def init_recognizer():
    global recognizer
    language = HOTKEY_CONFIG.get("language", "auto")
    recognizer = SenseVoiceRecognizer(language=language)


def on_activate():
    global target_window

    if audio_recorder.recording:
        audio_recorder.stop_recording()
        ipc.hide()
        audio_recorder.set_volume_callback(None)
        threading.Thread(target=transcribe_and_type, daemon=True).start()
    else:
        target_window = platform.get_focused_window()
        log(f"START_RECORDING window={target_window}")
        ipc.show_recording()
        audio_recorder.set_volume_callback(ipc.update_volume)
        audio_recorder.start_recording()


def transcribe_and_type():
    global target_window

    log(f"START_TRANSCRIBE")
    ipc.show_transcribing()

    try:
        audio_path = AudioRecorder.get_audio_path()
        text = recognizer.transcribe(audio_path)
        if text and text != ".":
            log(f"TRANSCRIBE_DONE text={text!r}")
            detected_lang = detect_language_from_text(text)
            record_transcription_language(detected_lang)
            log(f"HIDE_SPIN")
            ipc.hide()
            log(f"TYPE_TEXT_START text={text!r} window={target_window}")
            ipc.type_text(text, target_window)
            log(f"TYPE_TEXT_SENT")
        else:
            log("TRANSCRIBE_EMPTY")
            ipc.hide()
    except Exception as e:
        log(f"TRANSCRIBE_ERROR {e}")
        import traceback
        traceback.print_exc()
        ipc.hide()


def signal_handler(sig, frame):
    if audio_recorder.record_process:
        audio_recorder.record_process.terminate()
    log("EXITING")
    if keyboard_capture:
        keyboard_capture.stop()
    ipc.stop()
    sys.exit(0)


def main():
    global platform, keyboard_capture, recognizer

    VENV_PYTHON = SCRIPT_DIR / "venv-voice" / "bin" / "python3"
    if VENV_PYTHON.exists():
        venv_site = SCRIPT_DIR / "venv-voice" / "lib" / "python3.12" / "site-packages"
        if venv_site.exists() and str(venv_site) not in sys.path:
            sys.path.insert(0, str(venv_site))

    platform = PlatformTools(SESSION_TYPE)

    if SESSION_TYPE == 'x11' and not platform.xdotool_ok:
        print("Error: xdotool not installed")
        sys.exit(1)

    try:
        init_recognizer()
        log("RECOGNIZER_READY")
    except Exception as e:
        log(f"RECOGNIZER_ERROR {e}")
        sys.exit(1)

    ipc.start()
    log("IPC_STARTED")

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if SESSION_TYPE == 'x11':
        keyboard_capture = X11KeyboardCapture(on_activate)
    elif SESSION_TYPE == 'wayland':
        if platform.evdev_ok:
            keyboard_capture = WaylandKeyboardCapture(on_activate)
        else:
            log("WAYLAND_NO_EVDEV")
            sys.exit(1)
    else:
        keyboard_capture = X11KeyboardCapture(on_activate)

    if keyboard_capture:
        keyboard_capture.start()
    else:
        log("KEYBOARD_CAPTURE_ERROR")
        sys.exit(1)

    log(f"SERVICE_READY hotkey={HOTKEY_CONFIG['hotkey_mods']}+{HOTKEY_CONFIG['hotkey_key']}")

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
