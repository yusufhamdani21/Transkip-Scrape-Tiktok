import os
import sys
from pathlib import Path

from dotenv import load_dotenv

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        env_path = BASE_DIR / "_internal" / ".env"
else:
    BASE_DIR = Path(__file__).parent
    env_path = BASE_DIR / ".env"
load_dotenv(env_path)

DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "transkip.db"
RECORDINGS_DIR = DATA_DIR / "recordings"

DATA_DIR.mkdir(parents=True, exist_ok=True)
RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
RAPIDAPI_HOST = "tiktok-scraper7.p.rapidapi.com"

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
WHISPER_COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
