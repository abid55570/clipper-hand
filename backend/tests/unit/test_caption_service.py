"""Unit tests for caption service."""
import uuid
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.caption_service import start_transcription
from app.core.exceptions import VideoNotFoundError


class TestTranscription:
    @pytest.mark.asyncio
    async def test_start_transcription_video_not_found(self, mock_db_session):
        with patch("app.services.caption_service.get_video", return_value=None):
            with pytest.raises(VideoNotFoundError):
                await start_transcription(mock_db_session, uuid.uuid4())

    @pytest.mark.asyncio
    async def test_start_transcription_success(self, mock_db_session):
        mock_video = MagicMock()
        mock_video.id = uuid.uuid4()

        mock_caption = MagicMock()
        mock_caption.id = uuid.uuid4()

        mock_job = MagicMock()
        mock_job.id = uuid.uuid4()

        with patch("app.services.caption_service.get_video", return_value=mock_video), \
             patch("app.services.caption_service.create_caption", return_value=mock_caption), \
             patch("app.services.caption_service.create_job", return_value=mock_job), \
             patch("worker.tasks.caption_tasks.transcribe_video.delay", side_effect=Exception("No celery")):
            result = await start_transcription(mock_db_session, mock_video.id, "base")
            assert "job_id" in result
            assert "caption_id" in result
