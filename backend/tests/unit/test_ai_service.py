"""Unit tests for AI service."""
import uuid
import pytest
from unittest.mock import patch, MagicMock
from app.services.ai_service import start_highlight_detection, start_content_generation
from app.core.exceptions import VideoNotFoundError, ClipNotFoundError


class TestHighlightDetection:
    @pytest.mark.asyncio
    async def test_highlight_detection_video_not_found(self, mock_db_session):
        with patch("app.services.ai_service.get_video", return_value=None):
            with pytest.raises(VideoNotFoundError):
                await start_highlight_detection(mock_db_session, uuid.uuid4())

    @pytest.mark.asyncio
    async def test_highlight_detection_success(self, mock_db_session):
        mock_video = MagicMock()
        mock_video.id = uuid.uuid4()
        mock_job = MagicMock()
        mock_job.id = uuid.uuid4()

        with patch("app.services.ai_service.get_video", return_value=mock_video), \
             patch("app.services.ai_service.create_job", return_value=mock_job), \
             patch("worker.tasks.ai_tasks.detect_highlights.delay", side_effect=Exception("No celery")):
            result = await start_highlight_detection(mock_db_session, mock_video.id)
            assert "job_id" in result


class TestContentGeneration:
    @pytest.mark.asyncio
    async def test_content_generation_clip_not_found(self, mock_db_session):
        with patch("app.services.ai_service.get_clip", return_value=None):
            with pytest.raises(ClipNotFoundError):
                await start_content_generation(mock_db_session, uuid.uuid4())
