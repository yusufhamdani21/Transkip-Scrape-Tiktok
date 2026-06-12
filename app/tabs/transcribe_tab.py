import threading
import tempfile
from pathlib import Path

import flet as ft

from core.transcriber import transcribe, export_srt, export_vtt, get_available_models
from core.recorder import AudioRecorder
from core.database import save_transcription, get_transcriptions
from config import RECORDINGS_DIR


class TranscribeTab(ft.Column):
    def __init__(self, page):
        super().__init__(expand=True, spacing=10, scroll=ft.ScrollMode.AUTO)
        self._page = page
        self.recorder = AudioRecorder()
        self.audio_path = None
        self.segments = []
        self._build()

    def _build(self):
        self.file_picker = ft.FilePicker(on_result=self._on_file_picked)
        self._page.overlay.append(self.file_picker)

        self.model_dropdown = ft.Dropdown(
            label="Model Whisper",
            value="base",
            options=[ft.dropdown.Option(m) for m in get_available_models()],
            hint_text="Pilih model",
            width=200,
        )

        self.language_field = ft.TextField(
            label="Bahasa (kosongkan = auto)",
            hint_text="contoh: id, en, ja",
            width=200,
        )

        self.status_text = ft.Text("Siap", size=14, color=ft.colors.GREY_700)
        self.progress_bar = ft.ProgressBar(visible=False, width=600)

        self.result_text = ft.TextField(
            multiline=True,
            read_only=True,
            min_lines=10,
            max_lines=30,
            expand=True,
            hint_text="Hasil transkripsi akan muncul di sini...",
        )

        self.record_btn = ft.ElevatedButton(
            "Rekam Mikrofon",
            icon=ft.icons.MIC,
            on_click=self._toggle_record,
        )

        self.transcribe_btn = ft.ElevatedButton(
            "Transkrip",
            icon=ft.icons.TRANSCRIBE,
            on_click=self._transcribe,
            disabled=True,
        )

        self.export_dropdown = ft.Dropdown(
            value="TXT",
            options=[
                ft.dropdown.Option("TXT"),
                ft.dropdown.Option("SRT"),
                ft.dropdown.Option("VTT"),
            ],
            width=100,
        )

        self.export_btn = ft.ElevatedButton(
            "Export", icon=ft.icons.DOWNLOAD, on_click=self._export
        )

        controls = [
            ft.Row(
                [
                    ft.Text("Transkrip Audio", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            ft.Divider(),
            ft.Row(
                [
                    ft.ElevatedButton(
                        "Pilih File Audio",
                        icon=ft.icons.UPLOAD_FILE,
                        on_click=lambda _: self.file_picker.pick_files(
                            allow_multiple=False,
                            allowed_extensions=["mp3", "wav", "m4a", "ogg", "mp4", "webm"],
                            with_data=True,
                        ),
                    ),
                    self.record_btn,
                ],
                spacing=10,
            ),
            ft.Row(
                [self.model_dropdown, self.language_field],
                spacing=10,
            ),
            ft.Row(
                [self.transcribe_btn, self.export_dropdown, self.export_btn],
                spacing=10,
            ),
            self.status_text,
            self.progress_bar,
            self.result_text,
            ft.Text("Riwayat Transkripsi", style=ft.TextThemeStyle.TITLE_MEDIUM),
            ft.Divider(),
        ]
        self.controls = controls
        self._refresh_history()

    def _on_file_picked(self, e):
        if e.files and e.files[0]:
            f = e.files[0]
            if f.path:
                self.audio_path = f.path
            elif f.bytes:
                path = RECORDINGS_DIR / (f.name or f"upload_{id(f)}")
                path.write_bytes(f.bytes)
                self.audio_path = str(path)
            else:
                self.status_text.value = "Gagal: file tidak tersedia"
                self.status_text.color = ft.colors.RED
                self._page.update()
                return
            self.status_text.value = f"File: {f.name}"
            self.status_text.color = ft.colors.GREEN
            self.transcribe_btn.disabled = False
        elif e.path:
            self._save_result(e.path)
        self._page.update()

    def _save_result(self, path):
        if not path:
            return
        fmt = self.export_dropdown.value
        ext = fmt.lower()
        content = self.result_text.value
        if ext == "srt":
            content = export_srt(self.segments)
        elif ext == "vtt":
            content = export_vtt(self.segments)
        Path(path).write_text(content, encoding="utf-8")
        self.status_text.value = f"Terexport ke {path}"
        self.status_text.color = ft.colors.GREEN

    def _toggle_record(self, e):
        if not self.recorder.recording:
            self.recorder.start()
            self.record_btn.text = "Stop Rekaman"
            self.record_btn.icon = ft.icons.STOP
            self.status_text.value = "Merekam..."
            self.status_text.color = ft.colors.RED
            self.transcribe_btn.disabled = True
        else:
            result = self.recorder.stop()
            self.record_btn.text = "Rekam Mikrofon"
            self.record_btn.icon = ft.icons.MIC
            if result:
                self.audio_path, duration = result
                self.status_text.value = (
                    f"Rekaman selesai ({duration:.1f}s) - {Path(self.audio_path).name}"
                )
                self.status_text.color = ft.colors.GREEN
                self.transcribe_btn.disabled = False
            else:
                self.status_text.value = "Tidak ada audio direkam"
                self.status_text.color = ft.colors.ORANGE
        self._page.update()

    def _transcribe(self, e):
        if not self.audio_path:
            return

        self.transcribe_btn.disabled = True
        self.progress_bar.visible = True
        self.status_text.value = "Transkripsi sedang berlangsung..."
        self.status_text.color = ft.colors.BLUE
        self._page.update()

        def run():
            try:
                model_name = self.model_dropdown.value
                lang = self.language_field.value or None
                text, language, duration, segs = transcribe(
                    self.audio_path, model_name, lang
                )
                self.segments = segs
                filename = Path(self.audio_path).name

                save_transcription(filename, duration, text, language, model_name, segs)

                self.result_text.value = text
                self.status_text.value = (
                    f"Selesai! Bahasa: {language}, Durasi: {duration}s"
                )
                self.status_text.color = ft.colors.GREEN
            except Exception as ex:
                self.status_text.value = f"Error: {ex}"
                self.status_text.color = ft.colors.RED
            finally:
                self.transcribe_btn.disabled = False
                self.progress_bar.visible = False
                self._page.update()
                self._refresh_history()

        threading.Thread(target=run, daemon=True).start()

    def _export(self, e):
        if not self.result_text.value:
            return

        fmt = self.export_dropdown.value
        ext = fmt.lower()
        default_name = f"transkrip.{ext}"

        self.file_picker.save_file(
            dialog_title="Simpan hasil transkripsi",
            file_name=default_name,
        )

    def _refresh_history(self):
        try:
            records = get_transcriptions(10)
            history_col = ft.Column(spacing=4)
            for r in records:
                history_col.controls.append(
                    ft.ListTile(
                        title=ft.Text(r["filename"], size=13),
                        subtitle=ft.Text(
                            f"{r['created_at']} | {r['language']} | {r.get('duration', 0)}s",
                            size=11,
                        ),
                        leading=ft.Icon(ft.icons.DESCRIPTION),
                    )
                )
            if not history_col.controls:
                history_col.controls.append(ft.Text("Belum ada riwayat", italic=True))
            self.controls[-1] = history_col
            self._page.update()
        except Exception:
            pass
