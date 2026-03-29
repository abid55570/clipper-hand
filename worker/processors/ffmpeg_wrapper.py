"""Centralized FFmpeg operations wrapper."""
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Optional
import structlog

logger = structlog.get_logger(__name__)


def probe(input_path: str) -> dict:
    """Get video metadata via ffprobe."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format", "-show_streams",
            str(input_path),
        ],
        capture_output=True, text=True, timeout=60,
    )
    return json.loads(result.stdout)


def extract_segment(input_path: str, start: float, end: float, output_path: str) -> str:
    """Extract a segment from a video file."""
    duration = end - start
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start),
        "-i", str(input_path),
        "-t", str(duration),
        "-c:v", "libx264",
        "-c:a", "aac",
        "-movflags", "+faststart",
        "-preset", "medium",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg extract failed: {result.stderr[-500:]}")
    logger.info("segment_extracted", input=input_path, start=start, end=end, output=output_path)
    return output_path


def merge_segments(input_paths: list[str], output_path: str) -> str:
    """Merge multiple video segments into one."""
    # Create a concat file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for path in input_paths:
            f.write(f"file '{path}'\n")
        concat_file = f.name

    try:
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", concat_file,
            "-c:v", "libx264",
            "-c:a", "aac",
            "-movflags", "+faststart",
            str(output_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg merge failed: {result.stderr[-500:]}")
    finally:
        Path(concat_file).unlink(missing_ok=True)

    logger.info("segments_merged", count=len(input_paths), output=output_path)
    return output_path


def burn_ass_subtitles(input_path: str, ass_file: str, output_path: str) -> str:
    """Burn ASS subtitles into a video."""
    # Escape special characters in path for ffmpeg filter
    escaped_ass = ass_file.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-vf", f"ass={escaped_ass}",
        "-c:v", "libx264",
        "-c:a", "copy",
        "-preset", "medium",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg subtitle burn failed: {result.stderr[-500:]}")
    logger.info("subtitles_burned", input=input_path, output=output_path)
    return output_path


def resize_video(input_path: str, width: int, height: int, output_path: str,
                 crop_x: int = 0, crop_y: int = 0, crop_w: int = 0, crop_h: int = 0) -> str:
    """Resize video to target dimensions with optional crop."""
    if crop_w > 0 and crop_h > 0:
        # Crop then scale
        vf = f"crop={crop_w}:{crop_h}:{crop_x}:{crop_y},scale={width}:{height}"
    else:
        # Scale with padding to maintain aspect ratio
        vf = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black"

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-vf", vf,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-movflags", "+faststart",
        "-preset", "medium",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg resize failed: {result.stderr[-500:]}")
    logger.info("video_resized", width=width, height=height, output=output_path)
    return output_path


def extract_audio(input_path: str, output_path: str) -> str:
    """Extract audio from video as WAV."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg audio extraction failed: {result.stderr[-500:]}")
    return output_path


def detect_scene_changes(input_path: str, threshold: float = 0.3) -> list[float]:
    """Detect scene changes using ffmpeg's scene filter."""
    cmd = [
        "ffmpeg",
        "-i", str(input_path),
        "-vf", f"select='gt(scene,{threshold})',showinfo",
        "-f", "null", "-",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    timestamps = []
    for line in result.stderr.split("\n"):
        if "pts_time:" in line:
            try:
                pts = line.split("pts_time:")[1].split()[0]
                timestamps.append(float(pts))
            except (IndexError, ValueError):
                continue
    return timestamps


def remove_silence(input_path: str, output_path: str,
                   threshold_db: float = -40.0, min_silence: float = 0.5) -> str:
    """Remove silent sections from video (jump cuts)."""
    # First detect non-silent intervals
    cmd = [
        "ffmpeg", "-i", str(input_path),
        "-af", f"silencedetect=noise={threshold_db}dB:d={min_silence}",
        "-f", "null", "-",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)

    # Parse silence intervals
    silence_starts = []
    silence_ends = []
    for line in result.stderr.split("\n"):
        if "silence_start:" in line:
            try:
                ts = float(line.split("silence_start:")[1].strip().split()[0])
                silence_starts.append(ts)
            except (IndexError, ValueError):
                continue
        if "silence_end:" in line:
            try:
                ts = float(line.split("silence_end:")[1].strip().split()[0])
                silence_ends.append(ts)
            except (IndexError, ValueError):
                continue

    if not silence_starts:
        # No silence found, just copy
        subprocess.run(["cp", input_path, output_path], check=True)
        return output_path

    # Get video duration
    probe_data = probe(input_path)
    duration = float(probe_data.get("format", {}).get("duration", 0))

    # Build non-silent segments
    segments = []
    prev_end = 0.0
    for s_start, s_end in zip(silence_starts, silence_ends):
        if s_start > prev_end:
            segments.append((prev_end, s_start))
        prev_end = s_end
    if prev_end < duration:
        segments.append((prev_end, duration))

    if not segments:
        subprocess.run(["cp", input_path, output_path], check=True)
        return output_path

    # Extract and merge non-silent segments
    temp_files = []
    try:
        for i, (start, end) in enumerate(segments):
            temp_path = f"{output_path}.seg{i}.mp4"
            extract_segment(input_path, start, end, temp_path)
            temp_files.append(temp_path)

        if len(temp_files) == 1:
            Path(temp_files[0]).rename(output_path)
        else:
            merge_segments(temp_files, output_path)
    finally:
        for tf in temp_files:
            Path(tf).unlink(missing_ok=True)

    logger.info("silence_removed", segments=len(segments), output=output_path)
    return output_path


def add_zoom_effect(input_path: str, output_path: str,
                    zoom_start: float = 0, zoom_duration: float = 3,
                    zoom_factor: float = 1.3) -> str:
    """Add a zoom-in effect to a video segment."""
    probe_data = probe(input_path)
    video_stream = next((s for s in probe_data.get("streams", []) if s["codec_type"] == "video"), None)
    if not video_stream:
        raise RuntimeError("No video stream found")

    w = int(video_stream["width"])
    h = int(video_stream["height"])

    # zoompan filter for zoom-in effect
    fps = 30
    total_frames = int(zoom_duration * fps)
    vf = (
        f"zoompan=z='if(between(in_time,{zoom_start},{zoom_start + zoom_duration}),"
        f"min(zoom+{(zoom_factor - 1) / total_frames},{zoom_factor}),1)'"
        f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        f":d=1:s={w}x{h}:fps={fps}"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-vf", vf,
        "-c:v", "libx264",
        "-c:a", "copy",
        "-preset", "medium",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg zoom failed: {result.stderr[-500:]}")
    logger.info("zoom_effect_added", output=output_path)
    return output_path


def add_text_overlay(input_path: str, output_path: str,
                     text: str, font_size: int = 48,
                     position: str = "center",
                     start_time: float = 0, duration: float = 3,
                     animation: str = "fade") -> str:
    """Add text overlay with animation."""
    # Position mapping
    positions = {
        "top": "x=(w-text_w)/2:y=50",
        "center": "x=(w-text_w)/2:y=(h-text_h)/2",
        "bottom": "x=(w-text_w)/2:y=h-text_h-50",
    }
    pos = positions.get(position, positions["center"])

    # Animation: fade in/out
    enable = f"between(t,{start_time},{start_time + duration})"
    if animation == "fade":
        alpha = f"if(lt(t-{start_time},0.5),(t-{start_time})*2,if(gt(t-{start_time},{duration - 0.5}),({start_time + duration}-t)*2,1))"
    else:
        alpha = "1"

    # Escape text for ffmpeg
    safe_text = text.replace("'", "\\'").replace(":", "\\:")

    vf = f"drawtext=text='{safe_text}':fontsize={font_size}:fontcolor=white:borderw=3:bordercolor=black:{pos}:enable='{enable}':alpha='{alpha}'"

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-vf", vf,
        "-c:v", "libx264",
        "-c:a", "copy",
        "-preset", "medium",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg text overlay failed: {result.stderr[-500:]}")
    return output_path
