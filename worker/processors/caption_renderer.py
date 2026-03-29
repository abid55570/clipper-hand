"""ASS/SRT subtitle generation with styling and animations."""
import os
import tempfile
from pathlib import Path
import structlog

logger = structlog.get_logger(__name__)


def hex_to_ass_color(hex_color: str) -> str:
    """Convert #RRGGBB to ASS &HBBGGRR& format."""
    hex_color = hex_color.lstrip("#")
    r, g, b = hex_color[0:2], hex_color[2:4], hex_color[4:6]
    return f"&H00{b}{g}{r}&"


def generate_ass_subtitle(
    segments: list[dict],
    style_config: dict | None = None,
    output_path: str | None = None,
) -> str:
    """Generate an ASS subtitle file with styling.

    Args:
        segments: List of {start, end, text, words: [{word, start, end}]}
        style_config: Caption style configuration
        output_path: Where to save the ASS file

    Returns:
        Path to generated ASS file
    """
    config = style_config or {}
    font_family = config.get("font_family", "Arial")
    font_size = config.get("font_size", 48)
    primary_color = hex_to_ass_color(config.get("primary_color", "#FFFFFF"))
    outline_color = hex_to_ass_color(config.get("outline_color", "#000000"))
    highlight_color = hex_to_ass_color(config.get("highlight_color", "#FFFF00"))
    highlight_words = set(w.lower() for w in config.get("highlight_words", []))
    bold = config.get("bold", False)
    animation_type = config.get("animation_type", "none")
    position = config.get("position", "bottom")

    # Position mapping (ASS alignment)
    alignment_map = {"top": 8, "center": 5, "bottom": 2}
    alignment = alignment_map.get(position, 2)

    bold_flag = -1 if bold else 0

    if not output_path:
        fd, output_path = tempfile.mkstemp(suffix=".ass")
        os.close(fd)

    lines = []
    lines.append("[Script Info]")
    lines.append("Title: ClipperHand Captions")
    lines.append("ScriptType: v4.00+")
    lines.append("PlayResX: 1920")
    lines.append("PlayResY: 1080")
    lines.append("")
    lines.append("[V4+ Styles]")
    lines.append("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding")
    lines.append(f"Style: Default,{font_family},{font_size},{primary_color},&H000000FF&,{outline_color},&H80000000&,{bold_flag},0,0,0,100,100,0,0,1,3,1,{alignment},40,40,60,1")
    lines.append(f"Style: Highlight,{font_family},{font_size},{highlight_color},&H000000FF&,{outline_color},&H80000000&,{bold_flag},0,0,0,100,100,0,0,1,3,1,{alignment},40,40,60,1")
    lines.append("")
    lines.append("[Events]")
    lines.append("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text")

    for seg in segments:
        start_ts = _format_ass_time(seg["start"])
        end_ts = _format_ass_time(seg["end"])
        text = seg["text"]
        words = seg.get("words", [])

        if animation_type == "karaoke" and words:
            # Karaoke-style word-by-word reveal
            karaoke_text = _build_karaoke_text(words, highlight_words, highlight_color)
            lines.append(f"Dialogue: 0,{start_ts},{end_ts},Default,,0,0,0,,{karaoke_text}")

        elif animation_type == "word_by_word" and words:
            # Show words one at a time
            for word_info in words:
                w_start = _format_ass_time(word_info["start"])
                w_end = _format_ass_time(word_info["end"])
                word = word_info["word"]
                style = "Highlight" if word.lower().strip(".,!?") in highlight_words else "Default"
                lines.append(f"Dialogue: 0,{w_start},{w_end},{style},,0,0,0,,{word}")

        elif animation_type == "fade":
            # Fade in/out effect
            fade_text = f"{{\\fad(300,200)}}{_apply_highlights(text, highlight_words, highlight_color)}"
            lines.append(f"Dialogue: 0,{start_ts},{end_ts},Default,,0,0,0,,{fade_text}")

        elif animation_type == "pop":
            # Pop/scale effect
            pop_text = f"{{\\fscx50\\fscy50\\t(0,200,\\fscx100\\fscy100)}}{_apply_highlights(text, highlight_words, highlight_color)}"
            lines.append(f"Dialogue: 0,{start_ts},{end_ts},Default,,0,0,0,,{pop_text}")

        elif animation_type == "slide":
            # Slide up effect
            slide_text = f"{{\\move(960,600,960,540,0,300)}}{_apply_highlights(text, highlight_words, highlight_color)}"
            lines.append(f"Dialogue: 0,{start_ts},{end_ts},Default,,0,0,0,,{slide_text}")

        else:
            # No animation, just styled text
            styled_text = _apply_highlights(text, highlight_words, highlight_color)
            lines.append(f"Dialogue: 0,{start_ts},{end_ts},Default,,0,0,0,,{styled_text}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    logger.info("ass_subtitle_generated", output=output_path, segments=len(segments))
    return output_path


def generate_srt_subtitle(segments: list[dict], output_path: str | None = None) -> str:
    """Generate a simple SRT subtitle file."""
    if not output_path:
        fd, output_path = tempfile.mkstemp(suffix=".srt")
        os.close(fd)

    lines = []
    for i, seg in enumerate(segments, 1):
        start_ts = _format_srt_time(seg["start"])
        end_ts = _format_srt_time(seg["end"])
        lines.append(str(i))
        lines.append(f"{start_ts} --> {end_ts}")
        lines.append(seg["text"])
        lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return output_path


def _format_ass_time(seconds: float) -> str:
    """Format seconds as ASS timestamp: H:MM:SS.CC"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int((seconds % 1) * 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def _format_srt_time(seconds: float) -> str:
    """Format seconds as SRT timestamp: HH:MM:SS,mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _apply_highlights(text: str, highlight_words: set, highlight_color: str) -> str:
    """Apply color override to highlighted words in text."""
    if not highlight_words:
        return text
    result = []
    for word in text.split():
        clean = word.strip(".,!?;:\"'()[]").lower()
        if clean in highlight_words:
            result.append(f"{{\\c{highlight_color}}}{word}{{\\r}}")
        else:
            result.append(word)
    return " ".join(result)


def _build_karaoke_text(words: list[dict], highlight_words: set, highlight_color: str) -> str:
    """Build karaoke-style ASS text with timing per word."""
    parts = []
    for i, word_info in enumerate(words):
        duration_cs = int((word_info["end"] - word_info["start"]) * 100)
        word = word_info["word"]
        clean = word.strip(".,!?;:\"'()[]").lower()
        if clean in highlight_words:
            parts.append(f"{{\\kf{duration_cs}\\c{highlight_color}}}{word}")
        else:
            parts.append(f"{{\\kf{duration_cs}}}{word}")
    return " ".join(parts)
