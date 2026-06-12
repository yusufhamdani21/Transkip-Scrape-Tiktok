import json
from pathlib import Path
from faster_whisper import WhisperModel
from config import WHISPER_MODEL, WHISPER_DEVICE, WHISPER_COMPUTE_TYPE


model_cache = {}


def _get_model(model_name=None, device=None, compute_type=None):
    key = (model_name or WHISPER_MODEL, device or WHISPER_DEVICE)
    if key not in model_cache:
        model_cache[key] = WhisperModel(
            model_name or WHISPER_MODEL,
            device=device or WHISPER_DEVICE,
            compute_type=compute_type or WHISPER_COMPUTE_TYPE,
        )
    return model_cache[key]


def transcribe(audio_path, model_name=None, language=None):
    model = _get_model(model_name)
    segments, info = model.transcribe(str(audio_path), language=language)
    duration = round(info.duration, 2)
    lang = info.language

    segment_list = []
    full_text_parts = []
    for seg in segments:
        segment_list.append(
            {
                "start": round(seg.start, 2),
                "end": round(seg.end, 2),
                "text": seg.text.strip(),
            }
        )
        full_text_parts.append(seg.text.strip())

    full_text = " ".join(full_text_parts)
    return full_text, lang, duration, segment_list


def get_available_models():
    return ["tiny", "base", "small", "medium", "large-v3"]


def format_timestamp(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def export_srt(segments):
    lines = []
    for i, seg in enumerate(segments, 1):
        start = format_timestamp(seg["start"])
        end = format_timestamp(seg["end"])
        lines.append(f"{i}")
        lines.append(f"{start} --> {end}")
        lines.append(seg["text"])
        lines.append("")
    return "\n".join(lines)


def export_vtt(segments):
    lines = ["WEBVTT", ""]
    for seg in segments:
        start = format_timestamp(seg["start"]).replace(",", ".")
        end = format_timestamp(seg["end"]).replace(",", ".")
        lines.append(f"{start} --> {end}")
        lines.append(seg["text"])
        lines.append("")
    return "\n".join(lines)
