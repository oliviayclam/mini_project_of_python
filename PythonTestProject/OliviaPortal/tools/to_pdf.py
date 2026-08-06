"""Convert typed/uploaded text or speech audio into a PDF."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union

from tools.paths import ensure_tools_dir

DEFAULT_PDF_STYLE: Dict[str, Any] = {
    "title": "Olivia Portal",
    "font_family": "Helvetica",
    "font_size": 12,
    "title_size": 18,
    "align": "L",
    "line_height": 7,
    "text_color": "#132033",
    "title_color": "#1f5fbf",
    "margin": 18,
}


def _stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _hex_to_rgb(value: str, fallback=(19, 32, 51)):
    raw = (value or "").strip().lstrip("#")
    if len(raw) == 3:
        raw = "".join(ch * 2 for ch in raw)
    if len(raw) != 6:
        return fallback
    try:
        return tuple(int(raw[i : i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return fallback


def normalize_pdf_style(raw: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Clamp / normalize style values from a form or session."""
    src = raw or {}
    style = dict(DEFAULT_PDF_STYLE)

    raw_title = src.get("title", style["title"])
    if raw_title is None:
        title = style["title"]
    else:
        title = str(raw_title).strip() or style["title"]
    if title in {"None", "none", "null"}:
        title = style["title"]
    style["title"] = title[:80]

    family = str(src.get("font_family", style["font_family"]) or style["font_family"])
    style["font_family"] = family if family in {"Helvetica", "Times", "Courier"} else "Helvetica"

    try:
        style["font_size"] = max(8, min(28, int(src.get("font_size", style["font_size"]))))
    except (TypeError, ValueError):
        style["font_size"] = 12

    try:
        style["title_size"] = max(10, min(36, int(src.get("title_size", style["title_size"]))))
    except (TypeError, ValueError):
        style["title_size"] = 18

    align = str(src.get("align", style["align"]) or style["align"]).upper()
    style["align"] = align if align in {"L", "C", "R", "J"} else "L"

    try:
        style["line_height"] = max(5, min(16, int(src.get("line_height", style["line_height"]))))
    except (TypeError, ValueError):
        style["line_height"] = 7

    try:
        style["margin"] = max(10, min(40, int(src.get("margin", style["margin"]))))
    except (TypeError, ValueError):
        style["margin"] = 18

    style["text_color"] = str(src.get("text_color", style["text_color"]) or style["text_color"])
    style["title_color"] = str(src.get("title_color", style["title_color"]) or style["title_color"])
    return style


def text_to_pdf(
    text: str,
    output_path: Optional[Path] = None,
    style: Optional[Dict[str, Any]] = None,
) -> Path:
    """Write text into a styled multi-page PDF."""
    cleaned = (text or "").strip()
    if not cleaned:
        raise ValueError("Please enter or upload some text.")

    try:
        from fpdf import FPDF
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Package 'fpdf2' is missing. Activate OliviaPortal/.venv and run: "
            "pip install -r requirements.txt"
        ) from exc

    opts = normalize_pdf_style(style)
    ensure_tools_dir()
    path = output_path or (ensure_tools_dir() / f"export_{_stamp()}.pdf")

    safe_title = opts["title"].encode("latin-1", errors="replace").decode("latin-1")
    safe_body = cleaned.encode("latin-1", errors="replace").decode("latin-1")
    title_rgb = _hex_to_rgb(opts["title_color"], (31, 95, 191))
    text_rgb = _hex_to_rgb(opts["text_color"], (19, 32, 51))

    pdf = FPDF(orientation="L", format="A4")
    # Landscape page fits the side-by-side preview without tall scrolling.
    pdf.set_auto_page_break(auto=True, margin=opts["margin"])
    pdf.set_margins(opts["margin"], opts["margin"], opts["margin"])
    pdf.add_page()

    pdf.set_text_color(*title_rgb)
    pdf.set_font(opts["font_family"], "B", opts["title_size"])
    pdf.multi_cell(0, opts["title_size"] * 0.55, safe_title, align=opts["align"])
    pdf.ln(4)

    pdf.set_text_color(*text_rgb)
    pdf.set_font(opts["font_family"], size=opts["font_size"])
    pdf.multi_cell(0, opts["line_height"], safe_body, align=opts["align"])
    pdf.output(str(path))
    return path


def speech_to_text(audio_data: Union[bytes, Path], filename: str = "audio.wav") -> str:
    """Transcribe speech audio to text (uses free Google Web Speech API)."""
    try:
        import speech_recognition as sr
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Package 'SpeechRecognition' is missing. Activate OliviaPortal/.venv and run: "
            "pip install -r requirements.txt"
        ) from exc

    if isinstance(audio_data, Path):
        raw = audio_data.read_bytes()
        name = audio_data.name
    else:
        raw = audio_data
        name = filename or "audio.wav"

    if not raw:
        raise ValueError("Please upload a speech/audio file.")

    ensure_tools_dir()
    suffix = Path(name).suffix.lower() or ".wav"
    src = ensure_tools_dir() / f"speech_in_{_stamp()}{suffix}"
    src.write_bytes(raw)

    wav_path = src
    if suffix not in {".wav", ".flac", ".aiff", ".aif"}:
        try:
            from pydub import AudioSegment
            import imageio_ffmpeg

            AudioSegment.converter = imageio_ffmpeg.get_ffmpeg_exe()
            audio = AudioSegment.from_file(str(src))
            wav_path = ensure_tools_dir() / f"speech_in_{_stamp()}.wav"
            audio.export(str(wav_path), format="wav")
        except Exception as exc:
            raise ValueError(
                "Could not read this audio format. Try a .wav file, or install pydub."
            ) from exc

    recognizer = sr.Recognizer()
    with sr.AudioFile(str(wav_path)) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio)
    except sr.UnknownValueError as exc:
        raise ValueError("Could not understand the speech in this audio.") from exc
    except sr.RequestError as exc:
        raise ValueError(
            "Speech recognition service is unavailable. Check your internet connection."
        ) from exc

    text = (text or "").strip()
    if not text:
        raise ValueError("No speech text was recognized.")
    return text


def resolve_text_input(
    typed_text: str = "",
    text_file: Optional[bytes] = None,
    text_filename: str = "",
    audio_file: Optional[bytes] = None,
    audio_filename: str = "",
) -> str:
    """Pick text from textarea, uploaded .txt, or transcribed speech."""
    typed = (typed_text or "").strip()
    if typed:
        return typed

    if text_file:
        try:
            return text_file.decode("utf-8")
        except UnicodeDecodeError:
            return text_file.decode("latin-1", errors="replace")

    if audio_file:
        return speech_to_text(audio_file, filename=audio_filename or "audio.wav")

    raise ValueError("Provide typed text, a text file, or a speech/audio file.")


def style_from_form(form) -> Dict[str, Any]:
    """Build a style dict from a Flask request.form mapping."""
    return normalize_pdf_style(
        {
            "title": form.get("pdf_title"),
            "font_family": form.get("font_family"),
            "font_size": form.get("font_size"),
            "title_size": form.get("title_size"),
            "align": form.get("align"),
            "line_height": form.get("line_height"),
            "margin": form.get("margin"),
            "text_color": form.get("text_color"),
            "title_color": form.get("title_color"),
        }
    )
