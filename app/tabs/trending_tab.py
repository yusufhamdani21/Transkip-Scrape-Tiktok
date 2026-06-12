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


KEYWORD_SUGGESTIONS = [
    "artis", "seleb", "gosip", "viral", "drama",
    "selebriti", "aktor", "aktris", "penyanyi",
    "kawin", "cerai", "skandal", "pacaran",
    "bahlil",
    "politik", "presiden", "jokowi", "prabowo",
    "pemilu", "menteri", "dpr", "partai",
    "korupsi", "kabinet", "pemerintah", "rakyat",
]

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
        self._raw_videos = []
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
            icon=ft.icons.REFRESH,
            on_click=self._refresh_trending,
        )

        self.filter_field = ft.TextField(
            label="Filter kata kunci",
            hint_text="artis, gosip, politik...",
            on_change=self._on_filter_change,
            expand=True,
        )

        self.suggestion_chips = ft.Column(
            spacing=2,
            visible=False,
            wrap=True,
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
            icon=ft.icons.SAVE,
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
                    icon=ft.icons.TRENDING_UP,
                    on_click=lambda _: self._switch_inner_tab("feed"),
                ),
                ft.TextButton(
                    "Riwayat",
                    icon=ft.icons.HISTORY,
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
            self.filter_field,
            self.suggestion_chips,
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
            self.status_text.color = ft.colors.GREEN
            self._page.update()

    def _on_filter_change(self, e):
        text = self.filter_field.value.strip().lower()
        if not text:
            self.suggestion_chips.visible = False
            self._display_videos()
            self._page.update()
            return

        last_keyword = text.split(",")[-1].strip()
        if not last_keyword:
            self.suggestion_chips.visible = False
            self._display_videos()
            self._page.update()
            return

        matches = [kw for kw in KEYWORD_SUGGESTIONS if kw.startswith(last_keyword) and kw != last_keyword]
        self.suggestion_chips.controls.clear()
        if matches:
            for kw in matches[:10]:
                self.suggestion_chips.controls.append(
                    ft.TextButton(
                        kw,
                        on_click=lambda _, k=kw: self._apply_suggestion(k),
                    )
                )
        self.suggestion_chips.visible = bool(matches)
        self._display_videos()
        self._page.update()

    def _apply_suggestion(self, keyword):
        text = self.filter_field.value.strip()
        parts = [p.strip() for p in text.split(",") if p.strip()]
        if parts:
            parts[-1] = keyword
        else:
            parts = [keyword]
        self.filter_field.value = ", ".join(parts) + ", "
        self.suggestion_chips.visible = False
        self._display_videos()
        self._page.update()

    def _filter_videos(self):
        text = self.filter_field.value.strip().lower()
        if not text:
            return self._raw_videos[:]

        keywords = [kw.strip() for kw in text.split(",") if kw.strip()]
        if not keywords:
            return self._raw_videos[:]

        filtered = []
        for v in self._raw_videos:
            title = (v.get("title") or "").lower()
            if any(kw in title for kw in keywords):
                filtered.append(v)
        return filtered

    def _load_cached(self):
        region = self.region_dropdown.value
        cached = get_cached_trending(region)
        if cached:
            try:
                self._raw_videos = json.loads(cached["data"]) or []
                self._display_videos()
                self.status_text.value = f"Data cached dari {cached['fetched_at']}"
                self.status_text.color = ft.colors.GREY
                self._page.update()
            except Exception:
                pass

    def _refresh_trending(self, e):
        field_key = self.api_key_field.value.strip()
        if not field_key:
            self.status_text.value = "Masukkan RapidAPI Key terlebih dahulu"
            self.status_text.color = ft.colors.RED
            self._page.update()
            return

        self.client.api_key = field_key

        self.refresh_btn.disabled = True
        self.progress_bar.visible = True
        self.status_text.value = "Mengambil data trending..."
        self.status_text.color = ft.colors.BLUE
        self._page.update()

        def run():
            try:
                region = self.region_dropdown.value
                self._raw_videos = self.client.get_trending_feed(region)

                save_trending_cache(region, json.dumps(self._raw_videos, ensure_ascii=False))
                save_trending_history(region, self._raw_videos)

                filtered = self._filter_videos()
                self._display_videos()
                total = len(self._raw_videos)
                shown = len(filtered)
                label = REGIONS.get(region, region)
                if shown < total:
                    self.status_text.value = f"✅ {shown} dari {total} video ({label})"
                else:
                    self.status_text.value = f"✅ {total} video trending dari {label}"
                self.status_text.color = ft.colors.GREEN
            except Exception as ex:
                self.status_text.value = f"Error: {ex}"
                self.status_text.color = ft.colors.RED
            finally:
                self.refresh_btn.disabled = False
                self.progress_bar.visible = False
                self._page.update()
                self._refresh_history()

        threading.Thread(target=run, daemon=True).start()

    def _display_videos(self, videos=None):
        self.trending_list.controls.clear()
        source = videos if videos is not None else self._filter_videos()
        if not source:
            self.trending_list.controls.append(
                ft.Text("Tidak ada data trending", italic=True)
            )
            self.trending_list.update()
            return
        for i, v in enumerate(source[:20], 1):
            card = self._build_video_card(i, v)
            self.trending_list.controls.append(card)
        self.trending_list.update()

    def _build_video_card(self, rank, v):
        stats_row = ft.Row(
            [
                ft.Icon(ft.icons.FAVORITE_BORDER, size=14),
                ft.Text(self._format_num(v.get("likes", 0)), size=12),
                ft.Icon(ft.icons.CHAT_BUBBLE_OUTLINE, size=14),
                ft.Text(self._format_num(v.get("comments", 0)), size=12),
                ft.Icon(ft.icons.SHARE, size=14),
                ft.Text(self._format_num(v.get("shares", 0)), size=12),
                ft.Icon(ft.icons.PLAY_CIRCLE_OUTLINE, size=14),
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
                                        color=ft.colors.GREY_600,
                                    ),
                                    stats_row,
                                    ft.Row(
                                        [
                                            ft.Text(
                                                f"🎵 {v.get('music', '')[:40]}",
                                                size=11,
                                                color=ft.colors.GREY_600,
                                            ),
                                        ]
                                        + (
                                            [
                                                ft.Text(
                                                    f"#{v.get('hashtags', '')[:50]}",
                                                    size=11,
                                                    color=ft.colors.BLUE_400,
                                                )
                                            ]
                                            if v.get("hashtags", "")
                                            else []
                                        ),
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
            border=ft.border.all(1, ft.colors.GREY_300),
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
                    title = (r.get("title") or "")[:60]
                    self.history_list.controls.append(
                        ft.Text(f"  #{r['rank']} {title}", size=12)
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
