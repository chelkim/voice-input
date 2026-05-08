"""
SenseVoice speech recognition
"""
from pathlib import Path
from typing import Optional

import soundfile as sf


class SenseVoiceRecognizer:
    """SenseVoice speech recognizer"""

    def __init__(self, language: str = "auto"):
        """
        Args:
            language: Recognition language, can be auto, zh, en, ja, ko, yue
        """
        self.language = language
        self.recognizer = None
        self._init_recognizer()

    def _init_recognizer(self):
        """Initialize recognizer"""
        try:
            import sherpa_onnx
        except ImportError:
            raise RuntimeError("sherpa-onnx is not installed")

        model_path, tokens_path = self._get_model_files()
        print(f"Initializing recognizer, language mode: {self.language}")
        self.recognizer = sherpa_onnx.OfflineRecognizer.from_sense_voice(
            model=model_path,
            tokens=tokens_path,
            use_itn=True,
            debug=False,
            language=self.language,
        )

    def _get_model_files(self) -> tuple:
        """Find SenseVoice model files"""
        candidates = [
            Path(__file__).parent.parent.parent / "models",
            Path.home() / ".cache" / "sherpa-onnx-models",
            Path.home() / ".cache" / "huggingface" / "hub" / "models--lovemefan--SenseVoice-onnx",
        ]
        for d in candidates:
            model = d / "model.int8.onnx"
            tokens = d / "tokens.txt"
            if model.exists() and tokens.exists():
                return str(model), str(tokens)
        # Recursive search
        for p in Path.home().rglob("model.int8.onnx"):
            tokens = p.parent / "tokens.txt"
            if tokens.exists():
                return str(p), str(tokens)
        raise FileNotFoundError("SenseVoice model not found")

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe audio file.

        Args:
            audio_path: Path to audio file

        Returns:
            Recognized text
        """
        if self.recognizer is None:
            self._init_recognizer()

        print(f"Transcribing audio: {audio_path}", flush=True)
        print(f"Reading audio file...", flush=True)
        audio, sr = sf.read(audio_path, dtype="float32", always_2d=True)
        print(f"Audio sample rate: {sr}, duration: {len(audio)/sr:.2f}s", flush=True)
        audio = audio[:, 0]
        print("Creating recognition stream...", flush=True)
        stream = self.recognizer.create_stream()
        print("Starting recognition...", flush=True)
        stream.accept_waveform(sr, audio)
        self.recognizer.decode_stream(stream)
        result = stream.result.text.strip()
        print(f"Recognition complete, result: '{result}'", flush=True)
        return result

    @staticmethod
    def get_supported_languages() -> list:
        """Get list of supported languages"""
        return ["auto", "zh", "en", "ja", "ko", "yue"]
