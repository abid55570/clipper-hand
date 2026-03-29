"""Unit tests for clip service."""
import uuid
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.clip_service import create_clips_from_timestamps
from app.core.exceptions import VideoNotFoundError, InvalidTimestampError


class TestCreateClips:
    @pytest.mark.asyncio
    async def test_create_clips_video_not_found(self, mock_db_session):
        with patch("app.services.clip_service.get_video", return_value=None):
            with pytest.raises(VideoNotFoundError):
                await create_clips_from_timestamps(
                    mock_db_session,
                    uuid.uuid4(),
                    [{"start": 0, "end": 10}],
                )

    @pytest.mark.asyncio
    async def test_create_clips_invalid_timestamp(self, mock_db_session):
        mock_video = MagicMock()
        mock_video.duration_secs = 60.0
        mock_video.id = uuid.uuid4()

        with patch("app.services.clip_service.get_video", return_value=mock_video):
            with patch("app.services.clip_service.create_clip") as mock_create:
                mock_create.return_value = MagicMock(id=uuid.uuid4())
                with pytest.raises(InvalidTimestampError):
                    await create_clips_from_timestamps(
                        mock_db_session,
                        mock_video.id,
                        [{"start": 0, "end": 120}],  # Exceeds 60s duration
                    )

    @pytest.mark.asyncio
    async def test_create_clips_success(self, mock_db_session):
        mock_video = MagicMock()
        mock_video.duration_secs = 120.0
        mock_video.id = uuid.uuid4()

        mock_clip = MagicMock()
        mock_clip.id = uuid.uuid4()

        mock_job = MagicMock()
        mock_job.id = uuid.uuid4()

        with patch("app.services.clip_service.get_video", return_value=mock_video), \
             patch("app.services.clip_service.create_clip", return_value=mock_clip), \
             patch("app.services.clip_service.create_job", return_value=mock_job), \
             patch("worker.tasks.clip_tasks.batch_extract_clips.delay", side_effect=Exception("No celery")):
            result = await create_clips_from_timestamps(
                mock_db_session,
                mock_video.id,
                [{"start": 10, "end": 30, "label": "test"}],
            )
            assert "job_id" in result
            assert "clip_ids" in result
