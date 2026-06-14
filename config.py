import os
import sys
from pathlib import Path

from dotenv import load_dotenv

if getattr(sys, "frozen", False):
    env_path = Path(sys.executable).parent / ".env"
    if not env_path.exists():
        env_path = Path(sys.executable).parent / "_internal" / ".env"
    if not env_path.exists():
        env_path = Path(sys._MEIPASS) / ".env"
    DATA_DIR = Path(os.environ.get("APPDATA", Path.home())) / "Transkip" / "data"
else:
    env_path = Path(__file__).parent / ".env"
    DATA_DIR = Path(__file__).parent / "data"
load_dotenv(env_path)

DB_PATH = DATA_DIR / "transkip.db"
RECORDINGS_DIR = DATA_DIR / "recordings"

DATA_DIR.mkdir(parents=True, exist_ok=True)
RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
RAPIDAPI_HOST = "tiktok-scraper7.p.rapidapi.com"

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
WHISPER_COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
