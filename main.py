import sys
import os
import traceback

import flet as ft
from app.gui import main

if __name__ == "__main__":
    try:
        ft.app(target=main)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)
