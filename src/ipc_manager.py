#!/usr/bin/env python3
"""
IPC Manager - manages overlay process
"""
import subprocess
import json
import os


class IPCManager:
    def __init__(self):
        self._overlay_process = None
        self._started = False

    def start(self):
        """Start IPC processes"""
        if self._started:
            return
        self._started = True

        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Start overlay process with DISPLAY
        env = os.environ.copy()
        overlay_script = os.path.join(script_dir, "ui", "overlay_ipc.py")
        self._overlay_process = subprocess.Popen(
            ["python3", overlay_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env
        )

    def show_recording(self):
        """Show recording animation"""
        if self._overlay_process:
            msg = json.dumps({"cmd": "show_recording"}) + "\n"
            self._overlay_process.stdin.write(msg.encode())
            self._overlay_process.stdin.flush()

    def show_transcribing(self):
        """Show transcribing animation"""
        if self._overlay_process:
            msg = json.dumps({"cmd": "show_transcribing"}) + "\n"
            self._overlay_process.stdin.write(msg.encode())
            self._overlay_process.stdin.flush()

    def update_volume(self, volume):
        """Update volume for recording animation"""
        if self._overlay_process:
            msg = json.dumps({"cmd": "update_volume", "data": {"volume": float(volume)}}) + "\n"
            self._overlay_process.stdin.write(msg.encode())
            self._overlay_process.stdin.flush()

    def hide(self):
        """Hide overlay"""
        if self._overlay_process:
            msg = json.dumps({"cmd": "hide"}) + "\n"
            self._overlay_process.stdin.write(msg.encode())
            self._overlay_process.stdin.flush()

    def type_text(self, text, window_id=None):
        """Type text via clipboard + paste (runs in main process)"""
        from src.typing import type_text as do_type_text
        do_type_text(text)

    def stop(self):
        """Stop IPC processes"""
        if self._overlay_process:
            self._overlay_process.stdin.close()
            self._overlay_process.terminate()
