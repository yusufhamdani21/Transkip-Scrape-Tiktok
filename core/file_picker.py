import sys
from pathlib import Path


def _use_tkinter():
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        return filedialog
    except ImportError:
        return None


def pick_audio_file():
    fd = _use_tkinter()
    if fd:
        path = fd.askopenfilename(
            title="Pilih file audio",
            filetypes=[
                ("Audio files", "*.mp3 *.wav *.m4a *.ogg *.mp4 *.webm"),
                ("All files", "*.*"),
            ],
        )
        return path if path else None
    return None


def save_file(default_name="transkrip.txt"):
    fd = _use_tkinter()
    if fd:
        ext = Path(default_name).suffix
        path = fd.asksaveasfilename(
            title="Simpan hasil transkripsi",
            defaultextension=ext,
            filetypes=[
                ("Text", "*.txt"),
                ("SubRip", "*.srt"),
                ("WebVTT", "*.vtt"),
                ("All files", "*.*"),
            ],
            initialfile=default_name,
        )
        return path if path else None
    return None
