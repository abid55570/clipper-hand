"""Tests for FFmpeg wrapper module."""
import os
import subprocess
import pytest
from pathlib import Path


@pytest.fixture
def test_video(tmp_path):
    output = tmp_path / "test.mp4"
    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", "testsrc=duration=5:size=320x240:rate=15",
                "-f", "lavfi", "-i", "sine=frequency=440:duration=5",
                "-c:v", "libx264", "-c:a", "aac", "-shortest",
                str(output),
            ],
            capture_output=True, timeout=30, check=True,
        )
        return str(output)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("ffmpeg not available")


class TestProbe:
    def test_probe_returns_metadata(self, test_video):
        from worker.processors.ffmpeg_wrapper import probe
        result = probe(test_video)
        assert "streams" in result
        assert "format" in result
        assert float(result["format"]["duration"]) > 0


class TestExtractSegment:
    def test_extract_valid_segment(self, test_video, tmp_path):
        from worker.processors.ffmpeg_wrapper import extract_segment
        output = str(tmp_path / "segment.mp4")
        extract_segment(test_video, 0.5, 2.5, output)
        assert Path(output).exists()
        assert Path(output).stat().st_size > 0


class TestExtractAudio:
    def test_extract_audio_wav(self, test_video, tmp_path):
        from worker.processors.ffmpeg_wrapper import extract_audio
        output = str(tmp_path / "audio.wav")
        extract_audio(test_video, output)
        assert Path(output).exists()
