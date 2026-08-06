"""Remove image backgrounds and save a transparent PNG."""

from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Optional, Union

from PIL import Image

from tools.paths import ensure_tools_dir


def remove_background(
    image_data: Union[bytes, Path],
    output_path: Optional[Path] = None,
) -> Path:
    """Remove background from an image and save as PNG with transparency."""
    try:
        from rembg import remove
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Package 'rembg' is missing. Activate OliviaPortal/.venv and run: "
            "pip install -r requirements.txt"
        ) from exc

    if isinstance(image_data, Path):
        raw = image_data.read_bytes()
    else:
        raw = image_data

    if not raw:
        raise ValueError("Please upload an image.")

    result = remove(raw)
    img = Image.open(BytesIO(result)).convert("RGBA")

    ensure_tools_dir()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = output_path or (ensure_tools_dir() / f"nobg_{stamp}.png")
    img.save(path, format="PNG")
    return path
