"""
Base keyboard capture class
"""
from abc import ABC, abstractmethod
from typing import Callable


class BaseKeyboardCapture(ABC):
    """Abstract base class for keyboard capture"""

    def __init__(self, on_hotkey: Callable):
        """
        Args:
            on_hotkey: Callback function when hotkey is triggered
        """
        self.on_hotkey = on_hotkey
        self.running = False

    @abstractmethod
    def start(self):
        """Start keyboard capture"""
        pass

    @abstractmethod
    def stop(self):
        """Stop keyboard capture"""
        pass
