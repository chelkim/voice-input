"""
Platform abstraction layer.
Selects appropriate tools based on session type (X11/Wayland).
"""
import os
import subprocess
from abc import ABC, abstractmethod


class PlatformTools:
    """Platform tools abstraction"""

    def __init__(self, session_type: str):
        self.session = session_type
        self._check_tools()

    def _check_tools(self):
        """Check available tools"""
        self.xdotool_ok = self._cmd_exists('xdotool')
        self.ydotool_ok = self._cmd_exists('ydotool')
        self.xsel_ok = self._cmd_exists('xsel')
        self.wl_copy_ok = self._cmd_exists('wl-copy')
        self.evdev_ok = self._evdev_available()

        if self.session == 'wayland':
            if not self.ydotool_ok:
                print("Warning: ydotool not installed, keyboard simulation won't work on Wayland")
            if not self.evdev_ok:
                print("Warning: python-evdev not installed, hotkey capture won't work on Wayland")
            if not self.wl_copy_ok and not self.xsel_ok:
                print("Warning: No clipboard tool installed (need wl-copy or xsel)")
        else:
            if not self.xdotool_ok:
                print("Warning: xdotool not installed")

    def _cmd_exists(self, cmd: str) -> bool:
        """Check if command exists"""
        try:
            subprocess.run(['which', cmd], capture_output=True, check=True)
            return True
        except:
            return False

    def _evdev_available(self) -> bool:
        """Check if evdev is available"""
        try:
            import evdev
            return True
        except ImportError:
            return False

    # ---------- Clipboard ----------

    def clipboard_copy(self, text: str) -> bool:
        """Copy to clipboard"""
        try:
            # Use wayland tools on wayland, x11 tools on x11
            if self.session == 'wayland' and self.wl_copy_ok:
                p = subprocess.Popen(['wl-copy'], stdin=subprocess.PIPE)
                p.communicate(input=text.encode('utf-8'))
            elif self.xsel_ok:
                p = subprocess.Popen(['xsel', '--input', '--clipboard'], stdin=subprocess.PIPE)
                p.communicate(input=text.encode('utf-8'))
            else:
                print("Warning: No clipboard tool available")
                return False
            return True
        except Exception as e:
            print(f"Failed to copy to clipboard: {e}")
            return False

    def clipboard_paste(self) -> str:
        """Get content from clipboard"""
        try:
            if self.session == 'wayland' and self.wl_copy_ok:
                result = subprocess.run(['wl-paste'], capture_output=True, text=True)
                return result.stdout
            elif self.xsel_ok:
                result = subprocess.run(['xsel', '--output', '--clipboard'], capture_output=True, text=True)
                return result.stdout
        except Exception as e:
            print(f"Failed to read clipboard: {e}")
        return None

    # ---------- Window operations ----------

    def get_focused_window(self) -> str:
        """Get current focused window ID"""
        try:
            if self.session == 'wayland' and self.ydotool_ok:
                result = subprocess.run(['ydotool', 'getwindowfocus'],
                                       capture_output=True, text=True, timeout=1)
                return result.stdout.strip()
            elif self.xdotool_ok:
                result = subprocess.run(['xdotool', 'getwindowfocus'],
                                       capture_output=True, text=True, timeout=1)
                return result.stdout.strip()
        except Exception as e:
            print(f"Failed to get focused window: {e}")
        return None

    def focus_window(self, window_id: str) -> bool:
        """Activate specified window"""
        try:
            if self.session == 'wayland' and self.ydotool_ok:
                subprocess.run(['ydotool', 'windowfocus', '-f', window_id],
                             capture_output=True, timeout=3)
            elif self.xdotool_ok:
                subprocess.run(['xdotool', 'windowfocus', window_id],
                             capture_output=True, timeout=1)
            return True
        except Exception as e:
            print(f"Failed to focus window: {e}")
            return False

    def paste_text(self) -> bool:
        """Simulate Ctrl+Shift+V paste"""
        try:
            if self.session == 'wayland' and self.ydotool_ok:
                subprocess.run(['ydotool', 'key', 'ctrl+shift+v'],
                             capture_output=True, timeout=3)
            elif self.xdotool_ok:
                subprocess.run(['xdotool', 'key', '--clearmodifiers', 'ctrl+shift+v'],
                             capture_output=True, timeout=1)
            else:
                return False
            return True
        except Exception as e:
            print(f"Failed to paste: {e}")
            return False

    def type_text_async(self, text: str, window_id: str = None):
        """Type text using xdotool exec (non-blocking)"""
        import subprocess

        # Use xdotool exec to run typing in a subshell with its own X connection
        escaped = text.replace("'", "'\\''").replace('"', '\\"')
        subprocess.Popen(
            ['bash', '-c', f'xdotool type -- "{escaped}"'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
