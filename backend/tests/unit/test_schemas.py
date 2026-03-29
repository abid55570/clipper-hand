"""Unit tests for Pydantic schemas."""
import pytest
from pydantic import ValidationError
from app.schemas.clip import ClipTimestamp, CreateClipsRequest, TrimClipRequest
from app.schemas.video import UploadInitRequest
from app.schemas.caption import CaptionStyleRequest, TranscribeRequest
from app.schemas.export import ExportRequest, EffectsConfig


class TestClipTimestamp:
    def test_valid_timestamp(self):
        ts = ClipTimestamp(start=10.0, end=30.0, label="test")
        assert ts.start == 10.0
        assert ts.end == 30.0

    def test_end_before_start_raises(self):
        with pytest.raises(ValidationError):
            ClipTimestamp(start=30.0, end=10.0, label="invalid")

    def test_end_equals_start_raises(self):
        with pytest.raises(ValidationError):
            ClipTimestamp(start=10.0, end=10.0, label="zero")

    def test_negative_start_raises(self):
        with pytest.raises(ValidationError):
            ClipTimestamp(start=-5.0, end=10.0)


class TestCreateClipsRequest:
    def test_valid_request(self):
        req = CreateClipsRequest(clips=[
            ClipTimestamp(start=0, end=10, label="a"),
            ClipTimestamp(start=20, end=30, label="b"),
        ])
        assert len(req.clips) == 2

    def test_empty_clips_raises(self):
        with pytest.raises(ValidationError):
            CreateClipsRequest(clips=[])

    def test_too_many_clips_raises(self):
        clips = [ClipTimestamp(start=i, end=i+1, label=f"c{i}") for i in range(101)]
        with pytest.raises(ValidationError):
            CreateClipsRequest(clips=clips)


class TestTrimClipRequest:
    def test_valid_trim(self):
        req = TrimClipRequest(new_start=5.0, new_end=15.0)
        assert req.new_start == 5.0

    def test_invalid_trim(self):
        with pytest.raises(ValidationError):
            TrimClipRequest(new_start=15.0, new_end=5.0)


class TestUploadInitRequest:
    def test_valid_upload(self):
        req = UploadInitRequest(filename="video.mp4", file_size=1024000)
        assert req.filename == "video.mp4"

    def test_empty_filename_raises(self):
        with pytest.raises(ValidationError):
            UploadInitRequest(filename="", file_size=1024)

    def test_zero_size_raises(self):
        with pytest.raises(ValidationError):
            UploadInitRequest(filename="video.mp4", file_size=0)


class TestCaptionStyleRequest:
    def test_defaults(self):
        style = CaptionStyleRequest()
        assert style.font_family == "Arial"
        assert style.font_size == 48
        assert style.bold is False
        assert style.animation_type == "none"

    def test_invalid_color(self):
        with pytest.raises(ValidationError):
            CaptionStyleRequest(primary_color="red")

    def test_invalid_position(self):
        with pytest.raises(ValidationError):
            CaptionStyleRequest(position="left")

    def test_invalid_animation(self):
        with pytest.raises(ValidationError):
            CaptionStyleRequest(animation_type="bounce")

    def test_valid_karaoke(self):
        style = CaptionStyleRequest(
            animation_type="karaoke",
            bold=True,
            highlight_words=["hello", "world"],
            highlight_color="#FF0000",
        )
        assert style.animation_type == "karaoke"
        assert len(style.highlight_words) == 2


class TestTranscribeRequest:
    def test_defaults(self):
        req = TranscribeRequest()
        assert req.model_size == "base"

    def test_valid_model_sizes(self):
        for size in ["tiny", "base", "small", "medium", "large"]:
            req = TranscribeRequest(model_size=size)
            assert req.model_size == size

    def test_invalid_model_size(self):
        with pytest.raises(ValidationError):
            TranscribeRequest(model_size="huge")


class TestExportRequest:
    def test_valid_export(self):
        req = ExportRequest(aspect_ratio="9:16", platform="tiktok")
        assert req.aspect_ratio == "9:16"

    def test_invalid_aspect_ratio(self):
        with pytest.raises(ValidationError):
            ExportRequest(aspect_ratio="3:2")

    def test_with_effects(self):
        req = ExportRequest(
            aspect_ratio="1:1",
            effects=EffectsConfig(zoom=True, jump_cut=True),
        )
        assert req.effects.zoom is True
        assert req.effects.jump_cut is True

    def test_invalid_platform(self):
        with pytest.raises(ValidationError):
            ExportRequest(aspect_ratio="16:9", platform="facebook")
