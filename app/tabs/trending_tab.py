import threading
import json
from datetime import datetime

import flet as ft

from core.tiktok_client import TikTokClient
from core.database import (
    get_cached_trending,
    save_trending_cache,
    save_trending_history,
    get_trending_history,
)
from config import RAPIDAPI_KEY


REGIONS = {
    "ID": "Indonesia",
    "US": "Amerika Serikat",
    "JP": "Jepang",
    "KR": "Korea",
    "GB": "Inggris",
    "BR": "Brasil",
    "IN": "India",
    "MY": "Malaysia",
    "SG": "Singapura",
    "TH": "Thailand",
    "VN": "Vietnam",
    "PH": "Filipina",
    "TR": "Turki",
    "RU": "Rusia",
    "DE": "Jerman",
    "FR": "Prancis",
}


class TrendingTab(ft.Column):
    def __init__(self, page):
        super().__init__(expand=True, spacing=10, scroll=ft.ScrollMode.AUTO)
        self._page = page
        self.client = TikTokClient()
        self._build()

    def _build(self):
        self.region_dropdown = ft.Dropdown(
            label="Negara",
            value="ID",
            options=[ft.dropdown.Option(k, v) for k, v in REGIONS.items()],
            width=200,
        )

        self.refresh_btn = ft.ElevatedButton(
            "Refresh",
            icon=ft.Icons.REFRESH,
            on_click=self._refresh_trending,
        )

        self.status_text = ft.Text("", size=13)
        self.progress_bar = ft.ProgressBar(visible=False, width=600)

        self.api_key_field = ft.TextField(
            label="RapidAPI Key",
            value=RAPIDAPI_KEY,
            password=True,
            can_reveal_password=True,
            hint_text="Masukkan RapidAPI key Anda",
            on_submit=self._save_api_key,
            expand=True,
        )

        self.save_key_btn = ft.IconButton(
            icon=ft.Icons.SAVE,
            tooltip="Simpan API Key",
            on_click=self._save_api_key,
        )

        self.trending_list = ft.Column(spacing=8, expand=True)
        self.history_list = ft.Column(spacing=4)
        self.history_list.visible = False

        self.tab_btns = ft.Row(
            [
                ft.TextButton(
                    "Trending Feed",
                    icon=ft.Icons.TRENDING_UP,
                    on_click=lambda _: self._switch_inner_tab("feed"),
                ),
                ft.TextButton(
                    "Riwayat",
                    icon=ft.Icons.HISTORY,
                    on_click=lambda _: self._switch_inner_tab("history"),
                ),
            ],
            spacing=5,
        )

        controls = [
            ft.Text("Tren TikTok", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            ft.Divider(),
            ft.Row(
                [self.api_key_field, self.save_key_btn],
                spacing=5,
            ),
            ft.Row(
                [self.region_dropdown, self.refresh_btn],
                spacing=10,
            ),
            self.status_text,
            self.progress_bar,
            self.tab_btns,
            self.trending_list,
            self.history_list,
        ]
        self.controls = controls

        if self.client.is_configured:
            self._load_cached()

    def _switch_inner_tab(self, name):
        self.trending_list.visible = name == "feed"
        self.history_list.visible = name == "history"
        self._page.update()

    def _save_api_key(self, e=None):
        key = self.api_key_field.value.strip()
        if key:
            self.client.api_key = key
            self.status_text.value = "API Key tersimpan (untuk sesi ini)"
            self.status_text.color = ft.Colors.GREEN
            self._page.update()

    def _load_cached(self):
        region = self.region_dropdown.value
        cached = get_cached_trending(region)
        if cached:
            try:
                data = json.loads(cached["data"])
                self._display_videos(data)
                self.status_text.value = f"Data cached dari {cached['fetched_at']}"
                self.status_text.color = ft.Colors.GREY
                self._page.update()
            except Exception:
                pass

    def _refresh_trending(self, e):
        if not self.client.is_configured and not self.api_key_field.value:
            self.status_text.value = "Masukkan RapidAPI Key terlebih dahulu"
            self.status_text.color = ft.Colors.RED
            self._page.update()
            return

        if not self.client.is_configured:
            self.client.api_key = self.api_key_field.value.strip()

        self.refresh_btn.disabled = True
        self.progress_bar.visible = True
        self.status_text.value = "Mengambil data trending..."
        self.status_text.color = ft.Colors.BLUE
        self._page.update()

        def run():
            try:
                region = self.region_dropdown.value
                videos = self.client.get_trending_feed(region)

                save_trending_cache(region, json.dumps(videos, ensure_ascii=False))
                save_trending_history(region, videos)

                self._display_videos(videos)
                self.status_text.value = f"✅ {len(videos)} video trending dari {REGIONS.get(region, region)}"
                self.status_text.color = ft.Colors.GREEN
            except Exception as ex:
                self.status_text.value = f"Error: {ex}"
                self.status_text.color = ft.Colors.RED
            finally:
                self.refresh_btn.disabled = False
                self.progress_bar.visible = False
                self._page.update()
                self._refresh_history()

        threading.Thread(target=run, daemon=True).start()

    def _display_videos(self, videos):
        self.trending_list.controls.clear()
        for i, v in enumerate(videos[:20], 1):
            card = self._build_video_card(i, v)
            self.trending_list.controls.append(card)
        if not videos:
            self.trending_list.controls.append(
                ft.Text("Tidak ada data trending", italic=True)
            )
        self.trending_list.update()

    def _build_video_card(self, rank, v):
        stats_row = ft.Row(
            [
                ft.Icon(ft.Icons.FAVORITE_BORDER, size=14),
                ft.Text(self._format_num(v.get("likes", 0)), size=12),
                ft.Icon(ft.Icons.CHAT_BUBBLE_OUTLINE, size=14),
                ft.Text(self._format_num(v.get("comments", 0)), size=12),
                ft.Icon(ft.Icons.SHARE, size=14),
                ft.Text(self._format_num(v.get("shares", 0)), size=12),
                ft.Icon(ft.Icons.PLAY_CIRCLE_OUTLINE, size=14),
                ft.Text(self._format_num(v.get("plays", 0)), size=12),
            ],
            spacing=4,
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Text(f"#{rank}", size=16, weight=ft.FontWeight.BOLD),
                                width=40,
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        v.get("title", v.get("description", "No title"))[:80],
                                        size=14,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                    ft.Text(
                                        f"@{v.get('author', 'unknown')}",
                                        size=12,
                                        color=ft.Colors.GREY_600,
                                    ),
                                    stats_row,
                                    ft.Row(
                                        [
                                            ft.Text(
                                                f"🎵 {v.get('music', '')[:40]}",
                                                size=11,
                                                color=ft.Colors.GREY_600,
                                            ),
                                            ft.Text(
                                                f"#{v.get('hashtags', '')[:50]}",
                                                size=11,
                                                color=ft.Colors.BLUE_400,
                                            ),
                                        ],
                                        spacing=8,
                                    ),
                                ],
                                expand=True,
                                spacing=2,
                            ),
                        ],
                    ),
                    ft.Divider(height=1),
                ],
                spacing=4,
            ),
            padding=8,
            border=ft.Border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            ink=True,
            on_click=lambda _, url=v.get("url", ""): self._page.launch_url(url),
        )

    def _refresh_history(self):
        region = self.region_dropdown.value
        self.history_list.controls.clear()
        try:
            records = get_trending_history(region, 7)
            dates = set(r["fetched_date"] for r in records)
            for d in sorted(dates, reverse=True):
                day_videos = [r for r in records if r["fetched_date"] == d]
                self.history_list.controls.append(
                    ft.Text(
                        f"📅 {d} ({len(day_videos)} video)",
                        weight=ft.FontWeight.BOLD,
                        size=13,
                    )
                )
                for r in day_videos[:5]:
                    self.history_list.controls.append(
                        ft.Text(f"  #{r['rank']} {r['title'][:60]}", size=12)
                    )
                self.history_list.controls.append(ft.Divider(height=1))
            if not records:
                self.history_list.controls.append(
                    ft.Text("Belum ada riwayat", italic=True)
                )
        except Exception:
            self.history_list.controls.append(
                ft.Text("Gagal memuat riwayat", italic=True)
            )

    @staticmethod
    def _format_num(n):
        if n >= 1_000_000:
            return f"{n/1_000_000:.1f}M"
        if n >= 1_000:
            return f"{n/1_000:.1f}K"
        return str(n)
