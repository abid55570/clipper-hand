#!/usr/bin/env python3
"""Generate a small test video for CI/testing purposes."""
import subprocess
import sys
from pathlib import Path


def generate_test_video(output_path: str = "test_video.mp4", duration: int = 10):
    """Create a synthetic test video using ffmpeg."""
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"testsrc=duration={duration}:size=640x480:rate=30",
        "-f", "lavfi", "-i", f"sine=frequency=440:duration={duration}",
        "-c:v", "libx264", "-c:a", "aac",
        "-preset", "ultrafast",
        "-shortest",
        str(output_path),
    ]

    print(f"Generating test video: {output_path} ({duration}s)")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    size = Path(output_path).stat().st_size
    print(f"Generated: {output_path} ({size / 1024:.1f} KB)")


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else "test_video.mp4"
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    generate_test_video(output, duration)
