"""Extract text from PDFs and optionally convert to speech."""

from io import BytesIO
from pathlib import Path
from typing import Optional, Union

from pypdf import PdfReader

from tools.paths import ensure_tools_dir
from tools.text_media import text_to_speech


def pdf_to_text(pdf_data: Union[bytes, Path]) -> str:
    """Extract text from a PDF file."""
    if isinstance(pdf_data, Path):
        raw = pdf_data.read_bytes()
    else:
        raw = pdf_data

    if not raw:
        raise ValueError("Please upload a PDF.")

    reader = PdfReader(BytesIO(raw))
    parts = []
    for page in reader.pages:
        extracted = page.extract_text() or ""
        if extracted.strip():
            parts.append(extracted.strip())

    text = "\n\n".join(parts).strip()
    if not text:
        raise ValueError("No readable text found in this PDF.")
    return text


def pdf_to_speech(pdf_data: Union[bytes, Path], output_path: Optional[Path] = None) -> Path:
    """Extract PDF text and synthesize speech as MP3."""
    ensure_tools_dir()
    text = pdf_to_text(pdf_data)
    # gTTS has practical length limits; keep a reasonable chunk for demos
    if len(text) > 4500:
        text = text[:4500] + "..."
    return text_to_speech(text, output_path=output_path)
