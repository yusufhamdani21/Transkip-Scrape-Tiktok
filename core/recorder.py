import threading
import time
import wave
import tempfile
import os
from pathlib import Path

import numpy as np
import sounddevice as sd
from config import RECORDINGS_DIR


class AudioRecorder:
    def __init__(self, samplerate=16000, channels=1):
        self.samplerate = samplerate
        self.channels = channels
        self.recording = False
        self.audio_data = []
        self.thread = None
        self._stream = None

    def start(self):
        self.recording = True
        self.audio_data = []
        self._stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=self.channels,
            dtype=np.int16,
            callback=self._callback,
        )
        self._stream.start()

    def _callback(self, indata, frames, time_info, status):
        if self.recording:
            self.audio_data.append(indata.copy())

    def stop(self):
        self.recording = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        if not self.audio_data:
            return None

        data = np.concatenate(self.audio_data, axis=0)
        timestamp = int(time.time())
        filename = f"recording_{timestamp}.wav"
        filepath = str(RECORDINGS_DIR / filename)

        with wave.open(filepath, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)
            wf.setframerate(self.samplerate)
            wf.writeframes(data.tobytes())

        duration = len(data) / self.samplerate
        return filepath, duration
