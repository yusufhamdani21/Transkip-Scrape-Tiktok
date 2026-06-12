import os

import flet as ft
from app.gui import main

if __name__ == "__main__":
    view = os.getenv("FLET_VIEW", "flet_app")
    port = int(os.getenv("FLET_PORT", 8501))

    if view == "web":
        ft.run(main, port=port, view=ft.AppView.WEB_BROWSER)
    else:
        ft.run(main)
