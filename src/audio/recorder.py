"""
Audio recording module.
Uses sounddevice for real-time recording and volume calculation.
"""
import subprocess
import numpy as np
from pathlib import Path
from typing import Callable, List, Optional

# Audio file path
AUDIO_FILE = "/tmp/voice_input.wav"


class AudioRecorder:
    """Audio recorder"""

    def __init__(self, sample_rate: int = 16000):
        """
        Args:
            sample_rate: Sample rate, default 16000
        """
        self.sample_rate = sample_rate
        self.recording = False
        self.audio_stream = None
        self.record_process = None  # Fallback arecord process
        self.audio_data: List[np.ndarray] = []
        self._volume_callback: Optional[Callable] = None

    def set_volume_callback(self, callback: Callable):
        """Set volume callback function"""
        self._volume_callback = callback

    def _audio_callback(self, indata, frames, time, status):
        """Audio stream callback - calculates real-time volume and saves data"""
        if status:
            print(f"Audio status: {status}")
        # Save audio data
        self.audio_data.append(indata.copy())
        # Calculate volume (RMS)
        volume = np.sqrt(np.mean(indata**2))
        # Normalize to 0-1
        volume = min(1.0, volume * 5)
        if self._volume_callback:
            self._volume_callback(volume)

    def start_recording(self) -> bool:
        """Start recording"""
        if self.recording:
            return False

        self.audio_data = []
        try:
            import sounddevice as sd
            self.audio_stream = sd.InputStream(
                channels=1,
                samplerate=self.sample_rate,
                callback=self._audio_callback,
                dtype='float32'
            )
            self.audio_stream.start()
            self.recording = True
            return True
        except Exception as e:
            print(f"Failed to start recording: {e}")
            # Fallback to arecord
            self.record_process = subprocess.Popen(
                ["arecord", "-f", "cd", "-t", "wav", AUDIO_FILE],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.recording = True
            return True

    def stop_recording(self) -> Optional[str]:
        """
        Stop recording and save audio file.

        Returns:
            Audio file path, or None if failed
        """
        if not self.recording:
            return None

        self.recording = False

        if self.audio_stream:
            self.audio_stream.stop()
            self.audio_stream.close()
            self.audio_stream = None

            # Save audio to file
            if self.audio_data:
                import soundfile as sf
                audio = np.concatenate(self.audio_data, axis=0)
                sf.write(AUDIO_FILE, audio, self.sample_rate)
                print(f"Audio saved: {len(audio)} samples")
                self.audio_data = []
                return AUDIO_FILE
        elif self.record_process:
            self.record_process.terminate()
            self.record_process.wait()
            return AUDIO_FILE

        return None

    @staticmethod
    def get_audio_path() -> str:
        """Get audio file path"""
        return AUDIO_FILE
