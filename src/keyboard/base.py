"""
Base keyboard capture class
"""
from abc import ABC, abstractmethod
from typing import Callable, Optional


class BaseKeyboardCapture(ABC):
    """Abstract base class for keyboard capture"""

    def __init__(self, on_hotkey: Callable, on_cancel: Optional[Callable] = None):
        """
        Args:
            on_hotkey: Callback function when hotkey is triggered
            on_cancel: Optional callback when ESC is pressed during recording
        """
        self.on_hotkey = on_hotkey
        self.on_cancel = on_cancel
        self.running = False

    @abstractmethod
    def start(self):
        """Start keyboard capture"""
        pass

    @abstractmethod
    def stop(self):
        """Stop keyboard capture"""
        pass
