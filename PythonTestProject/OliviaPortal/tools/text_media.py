"""Convert text to speech (MP3) or a simple narrated video (MP4)."""

from datetime import datetime
from pathlib import Path
from textwrap import wrap
from typing import Optional

from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont

from tools.paths import ensure_tools_dir


def _stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def text_to_speech(text: str, output_path: Optional[Path] = None) -> Path:
    """Synthesize speech from text and save as MP3."""
    cleaned = (text or "").strip()
    if not cleaned:
        raise ValueError("Please enter some text.")

    ensure_tools_dir()
    path = output_path or (ensure_tools_dir() / f"speech_{_stamp()}.mp3")
    gTTS(text=cleaned, lang="en").save(str(path))
    return path


def _make_slide(text: str, size=(1280, 720)) -> Path:
    """Render text onto a simple slide image."""
    ensure_tools_dir()
    slide_path = ensure_tools_dir() / f"slide_{_stamp()}.png"

    img = Image.new("RGB", size, color=(19, 32, 51))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 42)
        title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 28)
    except OSError:
        font = ImageFont.load_default()
        title_font = font

    draw.text((60, 40), "Olivia Portal", fill=(143, 176, 227), font=title_font)

    lines = []
    for paragraph in text.strip().splitlines() or [text.strip()]:
        lines.extend(wrap(paragraph, width=42) or [""])
    lines = lines[:14]

    y = 140
    for line in lines:
        draw.text((60, y), line, fill=(232, 238, 248), font=font)
        y += 52

    img.save(slide_path)
    return slide_path


def text_to_video(text: str, output_path: Optional[Path] = None) -> Path:
    """Build an MP4: static text slide + spoken narration."""
    cleaned = (text or "").strip()
    if not cleaned:
        raise ValueError("Please enter some text.")

    try:
        from moviepy import AudioFileClip, ImageClip
    except ImportError:
        from moviepy.editor import AudioFileClip, ImageClip

    ensure_tools_dir()
    audio_path = ensure_tools_dir() / f"speech_{_stamp()}.mp3"
    text_to_speech(cleaned, output_path=audio_path)
    slide_path = _make_slide(cleaned)

    path = output_path or (ensure_tools_dir() / f"video_{_stamp()}.mp4")
    audio = AudioFileClip(str(audio_path))
    duration = max(float(audio.duration or 1.0), 1.0)
    clip = ImageClip(str(slide_path))
    # moviepy 2.x uses with_*; 1.x uses set_*
    if hasattr(clip, "with_duration"):
        clip = clip.with_duration(duration).with_audio(audio)
    else:
        clip = clip.set_duration(duration).set_audio(audio)
    clip.write_videofile(
        str(path),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        logger=None,
    )
    clip.close()
    audio.close()
    return path
