"""Unit tests for security module."""
import pytest
from app.core.security import (
    sanitize_filename,
    validate_video_extension,
    validate_file_size,
    validate_video_magic_bytes,
    ALLOWED_VIDEO_EXTENSIONS,
)
from app.core.exceptions import InvalidFileError, FileTooLargeError


class TestSanitizeFilename:
    def test_basic_filename(self):
        assert sanitize_filename("video.mp4") == "video.mp4"

    def test_path_traversal(self):
        result = sanitize_filename("../../etc/passwd")
        assert ".." not in result
        assert "etc" not in result

    def test_special_characters(self):
        result = sanitize_filename("my video (1) [final].mp4")
        assert result == "my_video__1___final_.mp4"

    def test_empty_filename(self):
        result = sanitize_filename("")
        assert result.endswith(".mp4") or len(result) > 0

    def test_dot_prefix(self):
        result = sanitize_filename(".hidden")
        assert not result.startswith(".")

    def test_with_directory_path(self):
        result = sanitize_filename("/some/path/video.mp4")
        assert "/" not in result
        assert result == "video.mp4"


class TestValidateVideoExtension:
    def test_valid_extensions(self):
        for ext in [".mp4", ".avi", ".mkv", ".mov", ".webm"]:
            validate_video_extension(f"video{ext}")  # Should not raise

    def test_invalid_extension(self):
        with pytest.raises(InvalidFileError):
            validate_video_extension("document.pdf")

    def test_invalid_extension_txt(self):
        with pytest.raises(InvalidFileError):
            validate_video_extension("script.py")

    def test_case_insensitive(self):
        validate_video_extension("video.MP4")  # Should not raise


class TestValidateFileSize:
    def test_valid_size(self):
        validate_file_size(1024 * 1024)  # 1 MB

    def test_too_large(self):
        with pytest.raises(FileTooLargeError):
            validate_file_size(100 * 1024 * 1024 * 1024)  # 100 GB


class TestValidateMagicBytes:
    def test_mp4_magic_bytes(self):
        # ftyp box in first 12 bytes
        header = b"\x00\x00\x00\x1cftypisom\x00\x00"
        validate_video_magic_bytes(header)  # Should not raise

    def test_mkv_magic_bytes(self):
        header = b"\x1aE\xdf\xa3\x00\x00\x00\x00\x00\x00\x00\x00"
        validate_video_magic_bytes(header)

    def test_invalid_magic_bytes(self):
        with pytest.raises(InvalidFileError):
            validate_video_magic_bytes(b"PK\x03\x04\x00\x00\x00\x00\x00\x00\x00\x00")  # ZIP file

    def test_avi_magic_bytes(self):
        header = b"RIFF\x00\x00\x00\x00AVI "
        validate_video_magic_bytes(header)
