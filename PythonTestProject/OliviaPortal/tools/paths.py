"""Shared output paths for tools."""

from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TOOLS_DIR = DATA_DIR / "tools"


def ensure_tools_dir() -> Path:
    TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    return TOOLS_DIR
