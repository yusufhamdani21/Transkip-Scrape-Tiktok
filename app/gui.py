import traceback
import os

import flet as ft

LOG_FILE = os.path.join(os.path.dirname(__file__) or ".", "transkip_error.log")


def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")


from app.tabs.transcribe_tab import TranscribeTab
from app.tabs.trending_tab import TrendingTab
from core.database import init_db


def _safe_create(page, label, factory):
    try:
        log(f"creating {label}...")
        tab = factory(page)
        log(f"{label} created OK")
        return tab
    except Exception as e:
        log(f"{label} FAILED: {e}\n{traceback.format_exc()}")
        return ft.Column(
            [
                ft.Text(f"Gagal memuat {label}", weight=ft.FontWeight.BOLD, color=ft.colors.RED),
                ft.Text(str(e), size=12),
                ft.Text(traceback.format_exc(), size=10, selectable=True),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )


def main(page: ft.Page):
    try:
        page.title = "Transkip - Audio Transkripsi & Tren TikTok"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 20
        page.window_width = 900
        page.window_height = 700
        page.window_min_width = 600
        page.window_min_height = 500

        log("init_db...")
        init_db()
        log("init_db done")

        nav = ft.Container(
            content=ft.Row(
                [
                    ft.Text("Transkip", size=22, weight=ft.FontWeight.BOLD),
                    ft.Text("Memuat...", size=12, color=ft.colors.GREY),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.only(bottom=10),
        )

        loading = ft.ProgressBar()
        page.add(nav, ft.Divider(), loading)
        page.update()

        transcribe_tab = _safe_create(page, "TranscribeTab", TranscribeTab)
        trending_tab = _safe_create(page, "TrendingTab", TrendingTab)

        if hasattr(trending_tab, "visible"):
            trending_tab.visible = False

        def switch_tab(name):
            if hasattr(transcribe_tab, "visible"):
                transcribe_tab.visible = name == "transcribe"
            if hasattr(trending_tab, "visible"):
                trending_tab.visible = name == "trending"
            page.update()

        nav.content = ft.Row(
            [
                ft.Text("Transkip", size=22, weight=ft.FontWeight.BOLD),
                ft.Row(
                    [
                        ft.TextButton(
                            "Transkrip Audio",
                            icon=ft.icons.TRANSCRIBE,
                            on_click=lambda _: switch_tab("transcribe"),
                        ),
                        ft.TextButton(
                            "Tren TikTok",
                            icon=ft.icons.TRENDING_UP,
                            on_click=lambda _: switch_tab("trending"),
                        ),
                    ],
                    spacing=5,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        page.controls.clear()
        page.add(nav, ft.Divider(), transcribe_tab, trending_tab)
        log("page.add done")
    except Exception as e:
        log(f"FATAL: {e}\n{traceback.format_exc()}")
        try:
            page.controls.clear()
            page.add(
                ft.Text("Fatal Error:", weight=ft.FontWeight.BOLD, color=ft.colors.RED),
                ft.Text(str(e)),
                ft.Container(
                    content=ft.Text(traceback.format_exc(), size=10, selectable=True),
                    scroll=ft.ScrollMode.AUTO,
                    height=300,
                ),
            )
            page.update()
        except Exception:
            pass
