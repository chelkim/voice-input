"""
Configuration module tests
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import _parse_hotkey, HOTKEY_CONFIG


def test_parse_hotkey():
    """Test hotkey parsing"""
    # Test Ctrl+Q
    mods, key = _parse_hotkey("Ctrl+Q")
    assert mods == ["ctrl"], f"Expected ['ctrl'], got {mods}"
    assert key == "q", f"Expected 'q', got {key}"

    # Test Ctrl+Alt+Q
    mods, key = _parse_hotkey("Ctrl+Alt+Q")
    assert mods == ["ctrl", "alt"], f"Expected ['ctrl', 'alt'], got {mods}"
    assert key == "q", f"Expected 'q', got {key}"

    # Test Meta+Q
    mods, key = _parse_hotkey("Meta+Q")
    assert mods == ["meta"], f"Expected ['meta'], got {mods}"
    assert key == "q", f"Expected 'q', got {key}"

    print("OK: _parse_hotkey tests passed")


def test_hotkey_config():
    """Test hotkey configuration"""
    assert isinstance(HOTKEY_CONFIG, dict), "HOTKEY_CONFIG should be a dict"
    assert "hotkey_mods" in HOTKEY_CONFIG, "HOTKEY_CONFIG should contain hotkey_mods"
    assert "hotkey_key" in HOTKEY_CONFIG, "HOTKEY_CONFIG should contain hotkey_key"
    assert HOTKEY_CONFIG["hotkey_key"] == "q", f"Expected 'q', got {HOTKEY_CONFIG['hotkey_key']}"
    print("OK: HOTKEY_CONFIG tests passed")


def test_supported_languages():
    """Test supported languages"""
    from src.recognition import SenseVoiceRecognizer
    languages = SenseVoiceRecognizer.get_supported_languages()
    assert "auto" in languages, "Should support auto"
    assert "zh" in languages, "Should support Chinese"
    assert "en" in languages, "Should support English"
    assert "ja" in languages, "Should support Japanese"
    assert "ko" in languages, "Should support Korean"
    assert "yue" in languages, "Should support Cantonese"
    print("OK: Supported languages list tests passed")


if __name__ == "__main__":
    test_parse_hotkey()
    test_hotkey_config()
    test_supported_languages()
    print("\nAll tests passed!")
