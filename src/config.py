"""
Configuration management module
"""
import configparser
import json
import re
from pathlib import Path
from typing import Dict

# Config file path
CONFIG_FILE = Path.home() / ".config" / "voice-input" / "config"
STATS_FILE = Path.home() / ".config" / "voice-input" / "language_stats.json"

# Language detection thresholds
LANGUAGE_DETECTION_THRESHOLD = 2  # Consecutive transcriptions in same language before updating UI

# Language usage statistics (persistent across restarts)
_language_stats = {
    "zh": 0,
    "en": 0,
    "ja": 0,
    "ko": 0,
    "yue": 0,
}
_last_detected_lang = None
_consecutive_count = 0


def _load_stats():
    """Load language stats from file"""
    global _language_stats
    try:
        if STATS_FILE.exists():
            with open(STATS_FILE, 'r') as f:
                _language_stats = json.load(f)
    except Exception as e:
        print(f"Failed to load language stats: {e}")


def _save_stats():
    """Save language stats to file"""
    try:
        STATS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATS_FILE, 'w') as f:
            json.dump(_language_stats, f)
    except Exception as e:
        print(f"Failed to save language stats: {e}")


def detect_language_from_text(text: str) -> str:
    """
    Detect language from transcribed text.
    Returns language code: zh, en, ja, ko, yue, or auto if uncertain.
    """
    if not text:
        return "auto"

    # Count character types
    chinese_chars = len(re.findall(r'[一-鿿]', text))  # Chinese characters
    japanese_chars = len(re.findall(r'[぀-ゟ゠-ヿ]', text))  # Hiragana/Katakana
    korean_chars = len(re.findall(r'[가-힯]', text))  # Hangul
    english_words = len(re.findall(r'[a-zA-Z]{2,}', text))  # English words

    total_chars = len(text)
    if total_chars == 0:
        return "auto"

    # Determine language based on character composition
    if chinese_chars / total_chars > 0.3:
        return "zh"
    elif japanese_chars / total_chars > 0.2:
        return "ja"
    elif korean_chars / total_chars > 0.3:
        return "ko"
    elif english_words > 0 and chinese_chars == 0 and japanese_chars == 0 and korean_chars == 0:
        return "en"

    # If mixed or uncertain, default to en
    return "en"


def record_transcription_language(lang: str):
    """
    Record a transcription in the given language and update UI if needed.
    """
    global _language_stats, _last_detected_lang, _consecutive_count

    # Skip if same as last detected
    if lang == _last_detected_lang:
        _consecutive_count += 1
    else:
        _last_detected_lang = lang
        _consecutive_count = 1

    _language_stats[lang] += 1
    _save_stats()

    # If we have enough consecutive detections, update UI language
    if _consecutive_count >= LANGUAGE_DETECTION_THRESHOLD and lang != "en":
        _update_config_ui_language(lang)
        print(f"Auto-detected language preference: {lang} (consecutive: {_consecutive_count})")
        # Reset consecutive count after update
        _consecutive_count = 0


def _update_config_ui_language(lang: str):
    """Update UI language in config file"""
    try:
        parser = configparser.ConfigParser()
        parser.read(CONFIG_FILE)

        if not parser.has_section("ui"):
            parser.add_section("ui")
        parser.set("ui", "language", lang)

        with open(CONFIG_FILE, 'w') as f:
            parser.write(f)
    except Exception as e:
        print(f"Failed to update UI language preference: {e}")


def load_config() -> Dict:
    """
    Load configuration from config file.

    Returns:
        Dict: Contains hotkey_mods, hotkey_key, language settings
    """
    # Load persistent stats
    _load_stats()

    config = {
        "hotkey_mods": ["ctrl"],
        "hotkey_key": "q",
        "language": "auto",  # Recognition language: auto, zh, en, ja, ko, yue
        "ui_language": "auto",  # UI display language: auto, zh, en, ja, ko, yue
    }

    # Ensure config directory exists
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

    if CONFIG_FILE.exists():
        try:
            parser = configparser.ConfigParser()
            parser.read(CONFIG_FILE)

            # Parse hotkey
            if parser.has_section("hotkey"):
                hotkey_str = parser.get("hotkey", "key", fallback="Ctrl+Q").strip()
                hotkey_mods, hotkey_key = _parse_hotkey(hotkey_str)
                config["hotkey_mods"] = hotkey_mods
                config["hotkey_key"] = hotkey_key
                print(f"Loaded hotkey from config: {hotkey_str}")

            # Parse recognition language setting
            if parser.has_section("recognition"):
                lang = parser.get("recognition", "language", fallback="auto").strip().lower()
                if lang in ("auto", "zh", "en", "ja", "ko", "yue"):
                    config["language"] = lang
                    print(f"Loaded language setting from config: {lang}")
                else:
                    print(f"Unknown language: {lang}, using default: auto")

            # Parse UI language setting
            if parser.has_section("ui"):
                ui_lang = parser.get("ui", "language", fallback="auto").strip().lower()
                if ui_lang in ("auto", "zh", "en", "ja", "ko", "yue"):
                    config["ui_language"] = ui_lang
                    print(f"Loaded UI language setting from config: {ui_lang}")

        except Exception as e:
            print(f"Failed to read config file: {e}")
    else:
        # Create default config file
        _create_default_config()

    return config


def _parse_hotkey(hotkey_str: str) -> tuple:
    """
    Parse hotkey string.

    Args:
        hotkey_str: Hotkey string, e.g. "Ctrl+Q"

    Returns:
        tuple: (hotkey_mods, hotkey_key)
    """
    # Normalize modifier key case
    parts = hotkey_str.replace("ctrl+", "Ctrl+")
    parts = parts.replace("alt+", "Alt+")
    parts = parts.replace("shift+", "Shift+")
    parts = parts.replace("meta+", "Meta+")

    keys = parts.split("+")
    hotkey_key = keys[-1].lower()  # Last key is the main key

    # Previous keys are modifiers
    hotkey_mods = []
    for k in keys[:-1]:
        k_lower = k.lower()
        if k_lower in ("ctrl", "control"):
            hotkey_mods.append("ctrl")
        elif k_lower in ("alt",):
            hotkey_mods.append("alt")
        elif k_lower in ("shift",):
            hotkey_mods.append("shift")
        elif k_lower in ("meta", "super", "win"):
            hotkey_mods.append("meta")

    return hotkey_mods, hotkey_key


def _create_default_config():
    """Create default configuration file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            f.write("[hotkey]\n")
            f.write("# Hotkey setting (modifiers+main key). Modifiers: ctrl, alt, shift, meta\n")
            f.write("key = Ctrl+Q\n")
            f.write("\n")
            f.write("[recognition]\n")
            f.write("# Language: auto, zh, en, ja, ko, yue\n")
            f.write("# auto will auto-detect language for speech recognition\n")
            f.write("language = auto\n")
            f.write("\n")
            f.write("[ui]\n")
            f.write("# UI display language: auto, zh, en, ja, ko, yue\n")
            f.write("# auto will auto-detect based on your speaking habits\n")
            f.write("language = auto\n")
        print(f"Created default config file: {CONFIG_FILE}")
    except Exception as e:
        print(f"Failed to create config file: {e}")


# Global config instance
HOTKEY_CONFIG = load_config()
