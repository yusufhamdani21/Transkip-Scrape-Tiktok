import sys
from pathlib import Path


def pick_audio_file():
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    path = filedialog.askopenfilename(
        title="Pilih file audio",
        filetypes=[
            ("Audio files", "*.mp3 *.wav *.m4a *.ogg *.mp4 *.webm"),
            ("All files", "*.*"),
        ],
    )
    root.destroy()
    return path if path else None


def save_file(default_name="transkrip.txt"):
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    path = filedialog.asksaveasfilename(
        title="Simpan hasil transkripsi",
        defaultextension=Path(default_name).suffix,
        filetypes=[
            ("Text", "*.txt"),
            ("SubRip", "*.srt"),
            ("WebVTT", "*.vtt"),
            ("All files", "*.*"),
        ],
        initialfile=default_name,
    )
    root.destroy()
    return path if path else None
