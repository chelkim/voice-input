#!/usr/bin/env python3
"""
Animation process - runs tkinter in a separate process.
"""
import sys
import json
import tkinter as tk
import time

LOG_FILE = "/tmp/overlay-log.txt"

def get_timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S.%%03d") % (time.time() % 1 * 1000)

def log(msg):
    ts = get_timestamp()
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{ts}] {msg}\n")

UI_TEXTS = {
    "zh": {"recording": "录音中...", "transcribing": "正在识别..."},
    "en": {"recording": "Recording...", "transcribing": "Transcribing..."},
}

class AnimationWindow:
    def __init__(self):
        self._root = None
        self._window = None
        self._canvas = None
        self._label = None
        self._spin_job = None
        self._pulse_job = None
        self._angle = 0
        self._bar_items = []
        self._current_volume = 0

    def create(self):
        self._root = tk.Tk()
        self._root.withdraw()

        self._window = tk.Toplevel(self._root)
        self._window.overrideredirect(True)
        self._window.attributes("-topmost", True)
        self._window.attributes("-alpha", 0.35)
        self._window.configure(bg="#16213e")
        self._window.withdraw()

        sw = self._window.winfo_screenwidth()
        sh = self._window.winfo_screenheight()
        ww, wh = 150, 52
        self._window.geometry(f"{ww}x{wh}+{(sw-ww)//2}+{sh-wh-100}")

        bg = tk.Canvas(self._window, width=ww, height=wh, bg="#16213e", highlightthickness=0)
        bg.pack()
        r = 12
        bg.create_rectangle(r, 0, ww-r, wh, fill="#16213e", outline="")
        bg.create_rectangle(0, r, ww, wh-r, fill="#16213e", outline="")
        bg.create_oval(-r, -r, r*2, r*2, fill="#16213e", outline="")
        bg.create_oval(ww-r*2, -r, ww+r, r*2, fill="#16213e", outline="")
        bg.create_oval(-r, wh-r*2, r*2, wh+r, fill="#16213e", outline="")
        bg.create_oval(ww-r*2, wh-r*2, ww+r, wh+r, fill="#16213e", outline="")

        self._canvas = tk.Canvas(bg, width=22, height=22, bg="#16213e", highlightthickness=0)
        self._canvas.place(x=12, y=15)

        self._label = tk.Label(bg, text="", font=("Microsoft YaHei", 11, "bold"),
                               fg="#e0e0e0", bg="#16213e")
        self._label.place(x=40, y=13)

    def _spin(self):
        if not self._window:
            return
        self._angle = (self._angle + 30) % 360
        self._canvas.delete("all")
        self._canvas.create_arc(2, 2, 20, 20, start=self._angle, extent=270,
                                style=tk.ARC, width=3, outline="#4ecdc4")
        self._spin_job = self._window.after(200, self._spin)

    def _pulse(self):
        if not self._window:
            return
        self._canvas.delete("all")
        heights = [6, 12, 16, 10, 6]
        xs = [2, 7, 12, 17, 22]
        for x, h in zip(xs, heights):
            self._canvas.create_rectangle(x, 22-h, x+3, 22, fill="#ff6b6b", outline="")
        self._pulse_job = self._window.after(120, self._pulse)

    def _animate_volume(self):
        if not self._window:
            return
        self._canvas.delete("all")
        xs = [2, 7, 12, 17, 22]
        max_h, min_h = 16, 4
        for i, x in enumerate(xs):
            pf = 1.0 - abs(i - 2) * 0.2
            h = min_h + (max_h - min_h) * self._current_volume * pf
            y_top = 22 - h
            self._bar_items[i] = self._canvas.create_rectangle(x, y_top, x+3, 22, fill="#ff6b6b", outline="")
        self._pulse_job = self._window.after(50, self._animate_volume)

    def _cancel(self):
        for job in [self._spin_job, self._pulse_job]:
            if job:
                self._window.after_cancel(job)
                job = None

    def show_recording(self):
        log("SHOW_RECORDING")
        self._cancel()
        self._label.config(text=UI_TEXTS["zh"]["recording"])
        self._canvas.delete("all")
        self._bar_items = [None, None, None, None, None]
        xs = [2, 7, 12, 17, 22]
        for i, x in enumerate(xs):
            self._bar_items[i] = self._canvas.create_rectangle(x, 22-6, x+3, 22, fill="#ff6b6b", outline="")
        self._window.deiconify()
        self._animate_volume()

    def update_volume(self, volume):
        self._current_volume = max(0, min(1, volume))

    def show_transcribing(self):
        log("SHOW_TRANSCRIBING")
        self._cancel()
        self._label.config(text=UI_TEXTS["zh"]["transcribing"])
        self._canvas.delete("all")
        self._window.deiconify()
        self._spin()

    def hide(self):
        log("HIDE")
        self._cancel()
        self._window.withdraw()

    def run(self):
        self.create()
        self._root.mainloop()


def main():
    log("OVERLAY_IPC_STARTED")
    win = AnimationWindow()

    def process_command(cmd, data):
        log(f"PROCESS_CMD {cmd}")
        if cmd == "show_recording":
            win.show_recording()
        elif cmd == "show_transcribing":
            win.show_transcribing()
        elif cmd == "hide":
            win.hide()
        elif cmd == "update_volume":
            win.update_volume(data.get("volume", 0))

    def read_commands():
        for line in sys.stdin:
            try:
                msg = json.loads(line.strip())
                cmd = msg.get("cmd", "")
                data = msg.get("data", {})
                log(f"RECV_CMD {cmd}")
                win._window.after(0, process_command, cmd, data)
            except:
                pass

    import threading
    t = threading.Thread(target=read_commands, daemon=True)
    t.start()

    win.run()

if __name__ == "__main__":
    main()
