"""Unit tests for custom exceptions."""
from app.core.exceptions import (
    AppError, VideoNotFoundError, ClipNotFoundError,
    JobNotFoundError, InvalidFileError, FileTooLargeError,
    ClipExtractionError, TranscriptionError, UploadNotFoundError,
    InvalidTimestampError, ExportNotFoundError, CaptionNotFoundError,
)


class TestExceptions:
    def test_app_error(self):
        err = AppError("test error", 500)
        assert err.message == "test error"
        assert err.status_code == 500
        assert str(err) == "test error"

    def test_video_not_found(self):
        err = VideoNotFoundError("abc-123")
        assert err.status_code == 404
        assert "abc-123" in err.message

    def test_clip_not_found(self):
        err = ClipNotFoundError("clip-456")
        assert err.status_code == 404

    def test_job_not_found(self):
        err = JobNotFoundError("job-789")
        assert err.status_code == 404

    def test_export_not_found(self):
        err = ExportNotFoundError("exp-123")
        assert err.status_code == 404

    def test_caption_not_found(self):
        err = CaptionNotFoundError("cap-123")
        assert err.status_code == 404

    def test_invalid_file(self):
        err = InvalidFileError("bad file type")
        assert err.status_code == 400
        assert "bad file type" in err.message

    def test_file_too_large(self):
        err = FileTooLargeError(10.0)
        assert err.status_code == 413
        assert "10" in err.message

    def test_clip_extraction_error(self):
        err = ClipExtractionError()
        assert err.status_code == 500

    def test_transcription_error(self):
        err = TranscriptionError("whisper failed")
        assert err.status_code == 500

    def test_upload_not_found(self):
        err = UploadNotFoundError("upload-abc")
        assert err.status_code == 404

    def test_invalid_timestamp(self):
        err = InvalidTimestampError("end before start")
        assert err.status_code == 400
