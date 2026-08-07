"""Convert PDF files to Word (.docx), preserving layout where possible."""

from datetime import datetime
from pathlib import Path
from typing import Optional, Union

from tools.paths import ensure_tools_dir


def _stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def pdf_to_word(
    pdf_data: Union[bytes, Path],
    output_path: Optional[Path] = None,
    source_name: str = "document.pdf",
) -> Path:
    """Convert a PDF to a Word document with layout close to the original."""
    try:
        from pdf2docx import Converter
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Package 'pdf2docx' is missing. Activate OliviaPortal/.venv and run: "
            "pip install -r requirements.txt"
        ) from exc

    if isinstance(pdf_data, Path):
        raw = pdf_data.read_bytes()
        name = pdf_data.name
    else:
        raw = pdf_data
        name = source_name or "document.pdf"

    if not raw:
        raise ValueError("Please upload a PDF.")

    ensure_tools_dir()
    stamp = _stamp()
    pdf_path = ensure_tools_dir() / f"pdf_in_{stamp}.pdf"
    pdf_path.write_bytes(raw)

    stem = Path(name).stem or "document"
    path = output_path or (ensure_tools_dir() / f"{stem}_{stamp}.docx")

    converter = Converter(str(pdf_path))
    try:
        # Keep layout/fonts/tables as close to the PDF as pdf2docx allows.
        converter.convert(str(path), start=0, end=None)
    finally:
        converter.close()

    if not path.exists() or path.stat().st_size == 0:
        raise ValueError("Could not convert this PDF to Word. Try another file.")
    return path
