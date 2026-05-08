"""
Overlay proxy - communicates with overlay process via stdin/stdout pipe.
"""
import subprocess
import threading
import json
import queue


class OverlayProxy:
    """
    Proxy for the overlay process.
    Communicates via stdin/stdout pipe to a separate process.
    """

    def __init__(self):
        self._process = None
        self._reader_thread = None
        self._running = False
        self._response_queue = queue.Queue()
        self._started = False

    def start(self):
        """Start the overlay process"""
        if self._started:
            return

        # Start overlay process with DISPLAY environment
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        overlay_script = os.path.join(script_dir, "overlay_process.py")

        env = os.environ.copy()
        if 'DISPLAY' not in env:
            env['DISPLAY'] = ':0'

        self._process = subprocess.Popen(
            ["python3", overlay_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=0,
            env=env
        )
        self._running = True
        self._started = True

        # Start reader thread
        self._reader_thread = threading.Thread(target=self._read_responses, daemon=True)
        self._reader_thread.start()

    def _send_command(self, cmd: str, data=None):
        """Send command to overlay process"""
        if not self._process or not self._running:
            return
        try:
            msg = json.dumps({"cmd": cmd, "data": data}) + "\n"
            self._process.stdin.write(msg.encode())
            self._process.stdin.flush()
        except Exception as e:
            print(f"Overlay send error: {e}")

    def _read_responses(self):
        """Read responses from overlay process"""
        if not self._process:
            return
        try:
            for line in self._process.stdout:
                if not self._running:
                    break
                # Responses are just for logging/debugging
                # print(f"Overlay: {line.decode().strip()}")
        except:
            pass

    def show_recording(self):
        """Show recording animation"""
        self._send_command("show_recording")

    def show_transcribing(self):
        """Show transcribing animation"""
        self._send_command("show_transcribing")

    def hide(self):
        """Hide overlay"""
        self._send_command("hide")

    def update_volume(self, volume: float):
        """Update volume display"""
        self._send_command("update_volume", {"volume": volume})

    def stop(self):
        """Stop the overlay process"""
        self._running = False
        if self._process:
            self._process.stdin.close()
            self._process.terminate()
            self._process.wait()
