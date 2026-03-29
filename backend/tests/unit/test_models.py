"""Unit tests for SQLAlchemy models."""
import uuid
from datetime import datetime, timezone
from app.models.video import Video
from app.models.clip import Clip
from app.models.job import Job
from app.models.caption import Caption, CaptionSegment, CaptionStyle
from app.models.export import Export, Highlight


class TestVideoModel:
    def test_video_creation(self):
        video = Video(
            filename="test.mp4",
            original_name="My Video.mp4",
            file_path="/uploads/test.mp4",
            file_size_bytes=1024000,
            status="uploading",
        )
        assert video.filename == "test.mp4"
        assert video.status == "uploading"

    def test_video_repr(self):
        video = Video(
            id=uuid.uuid4(),
            filename="test.mp4",
            original_name="My Video.mp4",
            file_path="/uploads/test.mp4",
            file_size_bytes=1024,
            status="ready",
        )
        repr_str = repr(video)
        assert "Video" in repr_str
        assert "ready" in repr_str


class TestClipModel:
    def test_clip_creation(self):
        clip = Clip(
            video_id=uuid.uuid4(),
            start_time=10.0,
            end_time=30.0,
            label="intro",
            status="pending",
        )
        assert clip.start_time == 10.0
        assert clip.computed_duration == 20.0

    def test_clip_repr(self):
        clip = Clip(
            id=uuid.uuid4(),
            video_id=uuid.uuid4(),
            start_time=5.0,
            end_time=15.0,
            status="ready",
        )
        repr_str = repr(clip)
        assert "Clip" in repr_str
        assert "5.0-15.0" in repr_str


class TestJobModel:
    def test_job_creation(self):
        job = Job(
            job_type="clip_extract",
            status="pending",
            progress_pct=0,
        )
        assert job.job_type == "clip_extract"
        assert job.progress_pct == 0

    def test_job_repr(self):
        job = Job(
            id=uuid.uuid4(),
            job_type="transcribe",
            status="running",
            progress_pct=50,
        )
        repr_str = repr(job)
        assert "transcribe" in repr_str
        assert "50%" in repr_str


class TestCaptionModels:
    def test_caption_creation(self):
        caption = Caption(
            video_id=uuid.uuid4(),
            model_size="base",
            status="pending",
        )
        assert caption.model_size == "base"

    def test_caption_segment(self):
        seg = CaptionSegment(
            caption_id=uuid.uuid4(),
            segment_index=0,
            start_time=0.0,
            end_time=5.0,
            text="Hello world",
        )
        assert seg.text == "Hello world"
        repr_str = repr(seg)
        assert "0" in repr_str

    def test_caption_style(self):
        style = CaptionStyle(
            caption_id=uuid.uuid4(),
            font_family="Arial",
            font_size=48,
            primary_color="#FFFFFF",
            outline_color="#000000",
            highlight_color="#FFFF00",
            position="bottom",
            bold=False,
            animation_type="none",
        )
        assert style.font_family == "Arial"


class TestExportModel:
    def test_export_creation(self):
        export = Export(
            clip_id=uuid.uuid4(),
            aspect_ratio="9:16",
            status="pending",
        )
        assert export.aspect_ratio == "9:16"

    def test_highlight_creation(self):
        highlight = Highlight(
            video_id=uuid.uuid4(),
            start_time=10.0,
            end_time=25.0,
            score=0.85,
            reason="High energy",
            source="audio_energy",
        )
        assert highlight.score == 0.85
        repr_str = repr(highlight)
        assert "0.85" in repr_str
