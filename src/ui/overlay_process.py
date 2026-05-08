#!/usr/bin/env python3
"""
Overlay process - runs tkinter in a separate process to avoid animation blocking.
Communicates with main process via stdin pipe.
"""
import sys
import os
import threading
import queue
import json
import tkinter as tk

# UI text
UI_TEXTS = {
    "auto": {"recording": "Recording...", "transcribing": "Transcribing..."},
    "zh": {"recording": "录音中...", "transcribing": "正在识别..."},
    "en": {"recording": "Recording...", "transcribing": "Transcribing..."},
    "ja": {"recording": "録音中...", "transcribing": "認識中..."},
    "ko": {"recording": "녹음 중...", "transcribing": "인식 중..."},
    "yue": {"recording": "錄音中...", "transcribing": "識別中..."},
}


def _get_ui_text(lang="zh"):
    return UI_TEXTS.get(lang, UI_TEXTS["en"])


class OverlayWindow:
    def __init__(self):
        self._root = None
        self._window = None
        self._canvas = None
        self._label = None
        self._pulse_job = None
        self._spin_job = None
        self._angle = 0
        self._current_volume = 0
        self._bar_items = []
        self._running = False
        self._action_queue = queue.Queue()

    def _create(self):
        self._root = tk.Tk()
        self._root.withdraw()

        self._window = tk.Toplevel(self._root)
        self._window.overrideredirect(True)
        self._window.attributes("-topmost", True)
        self._window.attributes("-alpha", 0.35)
        self._window.configure(bg="#16213e")
        self._window.withdraw()

        screen_w = self._window.winfo_screenwidth()
        screen_h = self._window.winfo_screenheight()
        win_w, win_h = 150, 52
        x = (screen_w - win_w) // 2
        y = screen_h - win_h - 100
        self._window.geometry(f"{win_w}x{win_h}+{x}+{y}")

        # Rounded background
        self._bg_canvas = tk.Canvas(self._window, width=win_w, height=win_h,
                                     bg="#16213e", highlightthickness=0)
        self._bg_canvas.pack()

        r = 12
        self._bg_canvas.create_rectangle(r, 0, win_w-r, win_h, fill="#16213e", outline="")
        self._bg_canvas.create_rectangle(0, r, win_w, win_h-r, fill="#16213e", outline="")
        self._bg_canvas.create_oval(-r, -r, r*2, r*2, fill="#16213e", outline="")
        self._bg_canvas.create_oval(win_w-r*2, -r, win_w+r, r*2, fill="#16213e", outline="")
        self._bg_canvas.create_oval(-r, win_h-r*2, r*2, win_h+r, fill="#16213e", outline="")
        self._bg_canvas.create_oval(win_w-r*2, win_h-r*2, win_w+r, win_h+r, fill="#16213e", outline="")

        self._canvas = tk.Canvas(self._bg_canvas, width=22, height=22,
                                  bg="#16213e", highlightthickness=0)
        self._canvas.place(x=12, y=15)

        self._bar_items = []
        x_positions = [2, 7, 12, 17, 22]
        for x in x_positions:
            bar = self._canvas.create_rectangle(x, 22-6, x+3, 22, fill="#ff6b6b", outline="")
            self._bar_items.append(bar)

        self._label = tk.Label(self._bg_canvas, text="",
                               font=("Microsoft YaHei", 11, "bold"),
                               fg="#e0e0e0", bg="#16213e")
        self._label.place(x=40, y=13)

    def _process_queue(self):
        try:
            while True:
                action = self._action_queue.get_nowait()
                action()
        except queue.Empty:
            pass
        if self._running:
            self._window.after(30, self._process_queue)

    def _animate_pulse(self):
        if not self._window:
            return
        self._pulse_up = not self._pulse_up
        self._canvas.delete("all")

        heights = [6, 12, 16, 10, 6] if self._pulse_up else [10, 8, 12, 8, 10]
        x_positions = [2, 7, 12, 17, 22]

        for x, h in zip(x_positions, heights):
            y_bottom = 22
            y_top = y_bottom - h
            self._canvas.create_rectangle(x, y_top, x+3, y_bottom, fill="#ff6b6b", outline="")

        self._pulse_job = self._window.after(120, self._animate_pulse)

    def _animate_volume(self):
        if not self._window:
            return

        volume = self._current_volume
        x_positions = [2, 7, 12, 17, 22]
        max_h, min_h = 16, 4

        for i, bar in enumerate(self._bar_items):
            position_factor = 1.0 - abs(i - 2) * 0.2
            h = min_h + (max_h - min_h) * volume * position_factor
            y_top = 22 - h
            self._canvas.coords(bar, x_positions[i], y_top, x_positions[i]+3, 22)

        self._pulse_job = self._window.after(50, self._animate_volume)

    def _animate_spin(self):
        if not self._window:
            return
        self._angle = (self._angle + 30) % 360
        self._canvas.delete("all")
        self._canvas.create_arc(2, 2, 20, 20,
                                 start=self._angle, extent=270,
                                 style=tk.ARC, width=3, outline="#4ecdc4")
        self._spin_job = self._window.after(80, self._animate_spin)

    def _cancel_anims(self):
        if self._pulse_job:
            self._window.after_cancel(self._pulse_job)
            self._pulse_job = None
        if self._spin_job:
            self._window.after_cancel(self._spin_job)
            self._spin_job = None

    def queue_action(self, action):
        self._action_queue.put(action)

    def show_recording(self):
        def action():
            self._cancel_anims()
            texts = _get_ui_text()
            self._label.config(text=texts["recording"])
            self._canvas.delete("all")
            self._bar_items = []
            x_positions = [2, 7, 12, 17, 22]
            for x in x_positions:
                bar = self._canvas.create_rectangle(x, 22-6, x+3, 22, fill="#ff6b6b", outline="")
                self._bar_items.append(bar)
            self._current_volume = 0
            self._window.deiconify()
            self._animate_volume()
        self.queue_action(action)

    def show_transcribing(self):
        def action():
            self._cancel_anims()
            texts = _get_ui_text()
            self._label.config(text=texts["transcribing"])
            self._canvas.delete("all")
            self._animate_spin()
            self._window.deiconify()
        self.queue_action(action)

    def hide(self):
        def action():
            self._cancel_anims()
            self._window.withdraw()
        self.queue_action(action)

    def update_volume(self, volume: float):
        def action():
            self._current_volume = max(0, min(1, volume))
        self.queue_action(action)

    def run(self):
        self._create()
        self._running = True
        self._process_queue()
        self._root.mainloop()

    def process_command(self, cmd: str, data=None):
        """Process a command from stdin"""
        if cmd == "show_recording":
            self.show_recording()
        elif cmd == "show_transcribing":
            self.show_transcribing()
        elif cmd == "hide":
            self.hide()
        elif cmd == "update_volume":
            if data and "volume" in data:
                self.update_volume(data["volume"])


def main():
    overlay = OverlayWindow()
    overlay.run()


if __name__ == "__main__":
    # If run with stdin pipe, read commands from it
    if not sys.stdin.isatty():
        overlay = OverlayWindow()
        overlay._create()
        overlay._running = True

        def read_commands():
            for line in sys.stdin:
                try:
                    msg = json.loads(line.strip())
                    cmd = msg.get("cmd", "")
                    data = msg.get("data")
                    if cmd == "show_recording":
                        overlay.show_recording()
                    elif cmd == "show_transcribing":
                        overlay.show_transcribing()
                    elif cmd == "hide":
                        overlay.hide()
                    elif cmd == "update_volume":
                        if data and "volume" in data:
                            overlay.update_volume(data["volume"])
                except:
                    pass

        thread = threading.Thread(target=read_commands, daemon=True)
        thread.start()

        overlay._root.mainloop()
    else:
        # Run standalone
        overlay = OverlayWindow()
        overlay.run()


if __name__ == "__main__":
    main()
