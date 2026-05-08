"""
X11 keyboard capture using pynput
"""
from pynput import keyboard
from typing import Callable, Set

from ..config import HOTKEY_CONFIG
from .base import BaseKeyboardCapture


class X11KeyboardCapture(BaseKeyboardCapture):
    """X11 keyboard capture using pynput"""

    def __init__(self, on_hotkey: Callable):
        super().__init__(on_hotkey)
        self.mods_pressed: Set[str] = set()  # Currently pressed modifier keys
        self.listener = None
        self.hotkey_key = HOTKEY_CONFIG["hotkey_key"]
        self.hotkey_mods = set(HOTKEY_CONFIG["hotkey_mods"])

    def _is_mod_key(self, key) -> str:
        """Check if key is a modifier, return modifier name"""
        mod_map = {
            "ctrl": (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r),
            "alt": (keyboard.Key.alt_l, keyboard.Key.alt_r),
            "shift": (keyboard.Key.shift_l, keyboard.Key.shift_r),
            "meta": (keyboard.Key.cmd_l, keyboard.Key.cmd_r),
        }
        for mod, keys in mod_map.items():
            if key in keys:
                return mod
        return None

    def start(self):
        def on_press(key):
            mod = self._is_mod_key(key)
            if mod:
                self.mods_pressed.add(mod)
            else:
                # Check if hotkey matches
                key_char = getattr(key, 'char', None)
                if key_char and key_char.lower() == self.hotkey_key:
                    if self.mods_pressed == self.hotkey_mods:
                        self.on_hotkey()

        def on_release(key):
            mod = self._is_mod_key(key)
            if mod:
                self.mods_pressed.discard(mod)

        self.listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.listener.start()

    def stop(self):
        if self.listener:
            self.listener.stop()
