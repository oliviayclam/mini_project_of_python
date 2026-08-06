"""Convert typed/uploaded text or speech audio into a PDF."""

from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Optional, Union

from tools.paths import ensure_tools_dir


def _stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def text_to_pdf(text: str, output_path: Optional[Path] = None) -> Path:
    """Write plain text into a simple multi-page PDF."""
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

    ensure_tools_dir()
    path = output_path or (ensure_tools_dir() / f"export_{_stamp()}.pdf")

    # FPDF core fonts are Latin-1; keep characters that render safely.
    safe = cleaned.encode("latin-1", errors="replace").decode("latin-1")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Olivia Portal", ln=True)
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 7, safe)
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
        # Convert mp3/m4a/etc to wav via pydub (uses ffmpeg from imageio-ffmpeg when present).
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
