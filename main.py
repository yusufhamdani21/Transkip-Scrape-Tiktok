import sys
import os
import traceback

import flet as ft
from app.gui import main
from config import RECORDINGS_DIR

if __name__ == "__main__":
    port = int(os.getenv("FLET_PORT", 8501))
    try:
        print(f"Transkip running at http://localhost:{port}")
        ft.app(
            target=main,
            port=port,
            view=ft.WEB_BROWSER,
            upload_dir=str(RECORDINGS_DIR),
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)
