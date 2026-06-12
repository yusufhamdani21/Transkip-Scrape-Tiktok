import traceback

import flet as ft

from app.tabs.transcribe_tab import TranscribeTab
from app.tabs.trending_tab import TrendingTab
from core.database import init_db


def main(page: ft.Page):
    try:
        page.title = "Transkip - Audio Transkripsi & Tren TikTok"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 20
        page.window_width = 900
        page.window_height = 700
        page.window_min_width = 600
        page.window_min_height = 500

        init_db()

        transcribe_tab = TranscribeTab(page)
        trending_tab = TrendingTab(page)
        trending_tab.visible = False

        def switch_tab(name):
            transcribe_tab.visible = name == "transcribe"
            trending_tab.visible = name == "trending"
            page.update()

        nav = ft.Container(
            content=ft.Row(
                [
                    ft.Text("Transkip", size=22, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        [
                            ft.TextButton(
                                "Transkrip Audio",
                                icon=ft.Icons.TRANSCRIBE,
                                on_click=lambda _: switch_tab("transcribe"),
                            ),
                            ft.TextButton(
                                "Tren TikTok",
                                icon=ft.Icons.TRENDING_UP,
                                on_click=lambda _: switch_tab("trending"),
                            ),
                        ],
                        spacing=5,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.Padding(0, 0, 0, 10),
        )

        page.add(nav, ft.Divider(), transcribe_tab, trending_tab)
    except Exception as e:
        page.add(
            ft.Text("Error saat memulai aplikasi:", weight=ft.FontWeight.BOLD, color=ft.Colors.RED),
            ft.Text(str(e)),
            ft.Text(traceback.format_exc(), size=10),
        )
        page.update()
