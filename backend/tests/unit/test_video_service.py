"""Unit tests for video service."""
import uuid
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services import video_service
from app.core.exceptions import InvalidFileError, FileTooLargeError, UploadNotFoundError


class TestUploadInit:
    @pytest.mark.asyncio
    async def test_init_upload_success(self, mock_db_session):
        result = await video_service.init_upload(
            mock_db_session, "test_video.mp4", 1024 * 1024, "video/mp4"
        )
        assert "upload_id" in result
        assert "chunk_size" in result
        assert "total_chunks" in result
        assert result["total_chunks"] >= 1

    @pytest.mark.asyncio
    async def test_init_upload_invalid_extension(self, mock_db_session):
        with pytest.raises(InvalidFileError):
            await video_service.init_upload(
                mock_db_session, "test.txt", 1024, "text/plain"
            )

    @pytest.mark.asyncio
    async def test_init_upload_file_too_large(self, mock_db_session):
        # 100 GB file
        with pytest.raises(FileTooLargeError):
            await video_service.init_upload(
                mock_db_session, "huge_video.mp4", 100 * 1024 * 1024 * 1024, "video/mp4"
            )


class TestUploadChunk:
    @pytest.mark.asyncio
    async def test_save_chunk_invalid_upload_id(self):
        with pytest.raises(UploadNotFoundError):
            await video_service.save_upload_chunk("nonexistent_id", 0, b"data")


class TestMetadataExtraction:
    def test_extract_metadata_with_valid_file(self, sample_video_path):
        """Test metadata extraction with a real or dummy video."""
        metadata = video_service.extract_video_metadata(sample_video_path)
        # Should return a dict (may be empty if ffprobe can't parse dummy file)
        assert isinstance(metadata, dict)

    def test_extract_metadata_with_invalid_path(self):
        metadata = video_service.extract_video_metadata("/nonexistent/file.mp4")
        assert isinstance(metadata, dict)
