"""Tests for processor modules."""
import pytest


class TestAIAnalyzer:
    def test_generate_content_from_transcript(self):
        from worker.processors.ai_analyzer import generate_content_from_transcript
        result = generate_content_from_transcript(
            "This is a great video about technology and innovation. "
            "We explore new ideas and breakthroughs.",
            60.0,
        )
        assert isinstance(result["title"], str)
        assert isinstance(result["description"], str)
        assert isinstance(result["hashtags"], list)
        assert len(result["title"]) > 0

    def test_generate_hooks(self):
        from worker.processors.ai_analyzer import generate_hooks
        hooks = generate_hooks("Amazing discovery in the field of science. "
                                "This changes everything we know.")
        assert len(hooks) >= 1
        for hook in hooks:
            assert "text" in hook
            assert "style" in hook

    def test_generate_content_empty_transcript(self):
        from worker.processors.ai_analyzer import generate_content_from_transcript
        result = generate_content_from_transcript("", 0)
        assert "title" in result
        assert "hashtags" in result


class TestCaptionRenderer:
    def test_hex_to_ass_color(self):
        from worker.processors.caption_renderer import hex_to_ass_color
        assert hex_to_ass_color("#FFFFFF") == "&H00FFFFFF&"
        assert hex_to_ass_color("#FF0000") == "&H000000FF&"
        assert hex_to_ass_color("#00FF00") == "&H0000FF00&"

    def test_format_ass_time(self):
        from worker.processors.caption_renderer import _format_ass_time
        assert _format_ass_time(0) == "0:00:00.00"
        assert _format_ass_time(65.5) == "0:01:05.50"
        assert _format_ass_time(3661.25) == "1:01:01.25"

    def test_format_srt_time(self):
        from worker.processors.caption_renderer import _format_srt_time
        assert _format_srt_time(0) == "00:00:00,000"
        assert _format_srt_time(65.5) == "00:01:05,500"


class TestSmartCrop:
    def test_crop_wider_to_taller(self):
        from worker.processors.smart_crop import calculate_smart_crop
        crop = calculate_smart_crop(1920, 1080, 1080, 1920)
        # Should crop width to match 9:16 ratio
        expected_w = int(1080 * (1080 / 1920))
        assert crop["w"] == expected_w
        assert crop["h"] == 1080

    def test_crop_taller_to_wider(self):
        from worker.processors.smart_crop import calculate_smart_crop
        crop = calculate_smart_crop(1080, 1920, 1920, 1080)
        assert crop["w"] == 1080
        assert crop["h"] <= 1920

    def test_crop_square(self):
        from worker.processors.smart_crop import calculate_smart_crop
        crop = calculate_smart_crop(1920, 1080, 1080, 1080)
        assert crop["w"] == 1080
        assert crop["h"] == 1080
