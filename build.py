import subprocess
import sys
from pathlib import Path


PYINSTALLER_CMD = [
    "pyinstaller",
    "--name=Transkip",
    "--windowed",
    "--onedir",
    "--add-data=.env;.",
    "--collect-all=faster_whisper",
    "--collect-all=ctranslate2",
    "--collect-all=torch",
    "--collect-all=nvidia",
    "--collect-all=flet",
    "--hidden-import=sounddevice",
    "--hidden-import=_sounddevice_data",
    "--hidden-import=requests",
    "--hidden-import=dotenv",
    "main.py",
]


def main():
    print("Membangun aplikasi Transkip dengan PyInstaller...")
    print("Perintah:", " ".join(PYINSTALLER_CMD))

    result = subprocess.run(PYINSTALLER_CMD, capture_output=False)
    if result.returncode == 0:
        print("\n✅ Build berhasil!")
        print(f"📦 Folder ada di: dist/Transkip/")
        print(f"   🚀 Jalankan Transkip.exe yang ada di dalam folder tersebut")
        print(f"   📌 Zip folder 'Transkip/' untuk dibagikan ke orang lain")
    else:
        print(f"\n❌ Build gagal dengan kode {result.returncode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
