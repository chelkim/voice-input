"""
Wayland keyboard capture using evdev
"""
import evdev
import threading
from typing import Callable, Set, Optional

from ..config import HOTKEY_CONFIG
from .base import BaseKeyboardCapture


class WaylandKeyboardCapture(BaseKeyboardCapture):
    """Wayland keyboard capture using evdev"""

    # Modifier keycode mappings
    MOD_KEYCODES = {
        "ctrl": [29, 97],   # KEY_LEFTCTRL, KEY_RIGHTCTRL
        "alt": [56, 100],   # KEY_LEFTALT, KEY_RIGHTALT
        "shift": [42, 54],  # KEY_LEFTSHIFT, KEY_RIGHTSHIFT
        "meta": [125, 126], # KEY_LEFTMETA, KEY_RIGHTMETA
    }

    # ESC key code
    ESC_KEYCODE = 1  # KEY_ESC

    def __init__(self, on_hotkey: Callable, on_cancel: Optional[Callable] = None):
        super().__init__(on_hotkey, on_cancel)
        self.mods_pressed: Set[str] = set()
        self.hotkey_key = HOTKEY_CONFIG["hotkey_key"].upper()
        self.hotkey_mods = set(HOTKEY_CONFIG["hotkey_mods"])
        self.keyboard_device = None
        self.thread = None
        self._find_keyboard()

    def _find_keyboard(self):
        """Find keyboard device"""
        self.keyboard_device = None

        hotkey_key_upper = self.hotkey_key.upper()
        key_code = getattr(evdev.ecodes, f'KEY_{hotkey_key_upper}', None)
        if key_code is None:
            print(f"Warning: Unknown key: {self.hotkey_key}")
            return

        # Scan all input devices, find keyboard (exclude virtual devices)
        for path in evdev.list_devices():
            try:
                dev = evdev.InputDevice(path)
                caps = dev.capabilities()

                # Skip virtual keyboard devices
                dev_name_lower = dev.name.lower()
                if 'ydotoold' in dev_name_lower or 'virtual' in dev_name_lower:
                    continue

                # Check if has keyboard capability (EV_KEY + target key)
                if 1 in caps:  # EV_KEY
                    keys = caps[1]
                    if key_code in keys:
                        self.keyboard_device = path
                        print(f"Found keyboard device: {path} ({dev.name})")
                        return
            except Exception:
                pass

        print("Warning: Keyboard device not found")

    def _get_key_code(self, key_name: str):
        """Get evdev keycode for a key"""
        key_upper = key_name.upper()
        return getattr(evdev.ecodes, f'KEY_{key_upper}', None)

    def start(self):
        if not self.keyboard_device:
            print("Warning: Keyboard device not found, hotkey capture may not work")
            return

        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

    def _capture_loop(self):
        try:
            dev = evdev.InputDevice(self.keyboard_device)

            # Get main key keycode
            hotkey_keycode = self._get_key_code(self.hotkey_key)
            if hotkey_keycode is None:
                print(f"Warning: Cannot get keycode for {self.hotkey_key}")
                return

            print(f"Keyboard capture started, listening on: {self.keyboard_device}", flush=True)
            print(f"Hotkey: {'+'.join(sorted(self.hotkey_mods))}+{self.hotkey_key} (keycode={hotkey_keycode})", flush=True)

            for event in dev.read_loop():
                if not self.running:
                    break
                if event.type == evdev.ecodes.EV_KEY:
                    # Check for ESC key
                    if event.code == self.ESC_KEYCODE and event.value == 1:
                        if self.on_cancel:
                            self.on_cancel()
                        continue

                    # Track modifier key state
                    for mod, codes in self.MOD_KEYCODES.items():
                        if event.code in codes:
                            if event.value == 1:  # Press
                                self.mods_pressed.add(mod)
                            elif event.value == 0:  # Release
                                self.mods_pressed.discard(mod)

                    # Check if main key is pressed
                    if event.code == hotkey_keycode and event.value == 1:
                        # Check if all modifiers are pressed
                        if self.mods_pressed == self.hotkey_mods:
                            print(f"*** {'+'.join(sorted(self.hotkey_mods))}+{self.hotkey_key} detected! ***", flush=True)
                            self.on_hotkey()
        except Exception as e:
            print(f"Keyboard capture error: {e}", flush=True)

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
