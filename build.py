import subprocess
import sys
from pathlib import Path


SEP = ";" if sys.platform == "win32" else ":"

PYINSTALLER_CMD = [
    "pyinstaller",
    "--name=Transkip",
    "--windowed",
    "--onefile",
    f"--add-data=.env{SEP}.env",
    "--hidden-import=faster_whisper",
    "--hidden-import=ctranslate2",
    "--hidden-import=sounddevice",
    "--hidden-import=_sounddevice_data",
    "--hidden-import=requests",
    "--hidden-import=dotenv",
    "--collect-all=flet",
    "main.py",
]


def main():
    print("Membangun aplikasi Transkip dengan PyInstaller...")
    print("Perintah:", " ".join(PYINSTALLER_CMD))

    result = subprocess.run(PYINSTALLER_CMD, capture_output=False)
    if result.returncode == 0:
        print("\n✅ Build berhasil!")
        print(f"📦 File ada di: dist/Transkip.exe")
    else:
        print(f"\n❌ Build gagal dengan kode {result.returncode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
