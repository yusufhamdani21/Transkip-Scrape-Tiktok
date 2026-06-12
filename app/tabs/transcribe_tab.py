import threading
from pathlib import Path

import flet as ft

from core.transcriber import transcribe, export_srt, export_vtt, get_available_models
from core.recorder import AudioRecorder
from core.database import save_transcription, get_transcriptions


class TranscribeTab(ft.Column):
    def __init__(self, page):
        super().__init__(expand=True, spacing=10, scroll=ft.ScrollMode.AUTO)
        self._page = page
        self.recorder = AudioRecorder()
        self.audio_path = None
        self.segments = []
        self._build()

    def _build(self):
        self.path_field = ft.TextField(
            label="Path file audio",
            hint_text="Klik Browse atau ketik path manual",
            expand=True,
            read_only=False,
        )

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

        self.status_text = ft.Text("Siap", size=14, color=ft.Colors.GREY_700)
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
            icon=ft.Icons.MIC,
            on_click=self._toggle_record,
        )

        self.transcribe_btn = ft.ElevatedButton(
            "Transkrip",
            icon=ft.Icons.TRANSCRIBE,
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
            "Export", icon=ft.Icons.DOWNLOAD, on_click=self._export
        )

        # Attempt to use FilePicker
        self.file_picker = None
        try:
            self.file_picker = ft.FilePicker()
            self._page.overlay.append(self.file_picker)
        except Exception:
            pass

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
                        "Browse",
                        icon=ft.Icons.UPLOAD_FILE,
                        on_click=self._pick_file,
                    ),
                    self.path_field,
                ],
                spacing=10,
                expand=True,
            ),
            ft.Row(
                [self.record_btn],
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

    def _pick_file(self, e):
        # Try FilePicker first
        if self.file_picker:
            try:
                files = self.file_picker.pick_files(
                    allow_multiple=False,
                    allowed_extensions=["mp3", "wav", "m4a", "ogg", "mp4", "webm"],
                )
                if files:
                    self.path_field.value = files[0].path
                    self._on_path_changed()
                return
            except Exception:
                pass

    def _on_path_changed(self):
        path = self.path_field.value.strip()
        if path and Path(path).exists():
            self.audio_path = path
            self.status_text.value = f"File: {Path(path).name}"
            self.status_text.color = ft.Colors.GREEN
            self.transcribe_btn.disabled = False
        else:
            self.audio_path = None
            self.status_text.value = "Siap"
            self.status_text.color = ft.Colors.GREY_700
            self.transcribe_btn.disabled = True
        self._page.update()

    def _toggle_record(self, e):
        if not self.recorder.recording:
            self.recorder.start()
            self.record_btn.text = "Stop Rekaman"
            self.record_btn.icon = ft.Icons.STOP
            self.status_text.value = "Merekam..."
            self.status_text.color = ft.Colors.RED
            self.transcribe_btn.disabled = True
        else:
            result = self.recorder.stop()
            self.record_btn.text = "Rekam Mikrofon"
            self.record_btn.icon = ft.Icons.MIC
            if result:
                self.audio_path, duration = result
                self.path_field.value = self.audio_path
                self.status_text.value = (
                    f"Rekaman selesai ({duration:.1f}s) - {Path(self.audio_path).name}"
                )
                self.status_text.color = ft.Colors.GREEN
                self.transcribe_btn.disabled = False
            else:
                self.status_text.value = "Tidak ada audio direkam"
                self.status_text.color = ft.Colors.ORANGE
        self._page.update()

    def _transcribe(self, e):
        if not self.audio_path:
            self._on_path_changed()
            if not self.audio_path:
                return

        self.transcribe_btn.disabled = True
        self.progress_bar.visible = True
        self.status_text.value = "Transkripsi sedang berlangsung..."
        self.status_text.color = ft.Colors.BLUE
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
                self.status_text.color = ft.Colors.GREEN
            except Exception as ex:
                self.status_text.value = f"Error: {ex}"
                self.status_text.color = ft.Colors.RED
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

        saved_path = None
        if self.file_picker:
            try:
                saved_path = self.file_picker.save_file(
                    dialog_title="Simpan hasil transkripsi",
                    file_name=default_name,
                )
            except Exception:
                pass

        if not saved_path:
            from tkinter import filedialog, Tk
            root = Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            saved_path = filedialog.asksaveasfilename(
                title="Simpan hasil transkripsi",
                defaultextension=f".{ext}",
                initialfile=default_name,
            )
            root.destroy()

        if not saved_path:
            return

        content = self.result_text.value
        if ext == "srt":
            content = export_srt(self.segments)
        elif ext == "vtt":
            content = export_vtt(self.segments)
        Path(saved_path).write_text(content, encoding="utf-8")
        self.status_text.value = f"Terexport ke {saved_path}"
        self.status_text.color = ft.Colors.GREEN
        self._page.update()

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
                        leading=ft.Icon(ft.Icons.DESCRIPTION),
                    )
                )
            if not history_col.controls:
                history_col.controls.append(ft.Text("Belum ada riwayat", italic=True))
            self.controls[-1] = history_col
            self._page.update()
        except Exception:
            pass
