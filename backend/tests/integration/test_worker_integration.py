"""Integration tests for worker processors."""
import os
import pytest
import tempfile
import subprocess
from pathlib import Path


class TestFFmpegWrapper:
    @pytest.fixture
    def test_video(self, tmp_path):
        """Create a test video."""
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

    def test_probe(self, test_video):
        from worker.processors.ffmpeg_wrapper import probe
        result = probe(test_video)
        assert "streams" in result
        assert "format" in result

    def test_extract_segment(self, test_video, tmp_path):
        from worker.processors.ffmpeg_wrapper import extract_segment
        output = str(tmp_path / "clip.mp4")
        extract_segment(test_video, 1.0, 3.0, output)
        assert os.path.exists(output)
        assert os.path.getsize(output) > 0

    def test_extract_audio(self, test_video, tmp_path):
        from worker.processors.ffmpeg_wrapper import extract_audio
        output = str(tmp_path / "audio.wav")
        extract_audio(test_video, output)
        assert os.path.exists(output)
        assert os.path.getsize(output) > 0


class TestCaptionRenderer:
    def test_generate_ass_subtitle(self, sample_transcript_segments, tmp_path):
        from worker.processors.caption_renderer import generate_ass_subtitle
        output = str(tmp_path / "test.ass")
        result = generate_ass_subtitle(
            sample_transcript_segments,
            {"font_family": "Arial", "font_size": 48, "animation_type": "none"},
            output,
        )
        assert os.path.exists(result)
        content = Path(result).read_text()
        assert "[Script Info]" in content
        assert "Dialogue:" in content

    def test_generate_srt_subtitle(self, sample_transcript_segments, tmp_path):
        from worker.processors.caption_renderer import generate_srt_subtitle
        output = str(tmp_path / "test.srt")
        result = generate_srt_subtitle(sample_transcript_segments, output)
        assert os.path.exists(result)
        content = Path(result).read_text()
        assert "-->" in content

    def test_karaoke_animation(self, sample_transcript_segments, tmp_path):
        from worker.processors.caption_renderer import generate_ass_subtitle
        output = str(tmp_path / "karaoke.ass")
        result = generate_ass_subtitle(
            sample_transcript_segments,
            {"animation_type": "karaoke", "highlight_words": ["welcome", "amazing"]},
            output,
        )
        content = Path(result).read_text()
        assert "\\kf" in content  # Karaoke timing tags


class TestAIAnalyzer:
    def test_generate_content_from_transcript(self):
        from worker.processors.ai_analyzer import generate_content_from_transcript
        result = generate_content_from_transcript(
            "Hello world. This is a test video about machine learning and AI. "
            "We discuss deep learning techniques.",
            30.0,
        )
        assert "title" in result
        assert "description" in result
        assert "hashtags" in result
        assert len(result["hashtags"]) > 0

    def test_generate_hooks(self):
        from worker.processors.ai_analyzer import generate_hooks
        result = generate_hooks("This is an amazing discovery in science. "
                                "Researchers found a breakthrough method.")
        assert len(result) > 0
        assert "text" in result[0]
        assert "style" in result[0]


class TestSmartCrop:
    def test_calculate_smart_crop_16_9_to_9_16(self):
        from worker.processors.smart_crop import calculate_smart_crop
        crop = calculate_smart_crop(1920, 1080, 1080, 1920)
        assert crop["w"] > 0
        assert crop["h"] > 0
        assert crop["w"] <= 1920
        assert crop["h"] <= 1080

    def test_calculate_smart_crop_same_ratio(self):
        from worker.processors.smart_crop import calculate_smart_crop
        crop = calculate_smart_crop(1920, 1080, 1920, 1080)
        assert crop["x"] == 0
        assert crop["y"] == 0

    def test_calculate_smart_crop_with_face(self):
        from worker.processors.smart_crop import calculate_smart_crop
        crop = calculate_smart_crop(1920, 1080, 1080, 1920, face_center=(960, 540))
        assert crop["w"] > 0
        assert crop["h"] > 0
