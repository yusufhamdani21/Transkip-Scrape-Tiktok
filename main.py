import sys
import os
import traceback

import flet as ft
from app.gui import main

LOG_FILE = os.path.join(os.path.dirname(__file__) or ".", "transkip_error.log")
PORT = int(os.getenv("FLET_PORT", 8501))


if __name__ == "__main__":
    try:
        with open(LOG_FILE, "w") as f:
            f.write("Starting Transkip in WEB mode...\n")
            f.write(f"Open http://localhost:{PORT} in your browser\n")

        ft.run(
            main,
            port=PORT,
            view=ft.AppView.WEB_BROWSER,
        )
    except Exception as e:
        with open(LOG_FILE, "a") as f:
            f.write(f"Error: {e}\n{traceback.format_exc()}\n")
        print(f"Error: {e}", file=sys.stderr)
        print(f"Check {LOG_FILE} for details", file=sys.stderr)
        sys.exit(1)
