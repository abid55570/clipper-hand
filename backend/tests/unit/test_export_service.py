"""Unit tests for export service."""
import uuid
import pytest
from unittest.mock import patch, MagicMock
from app.services.export_service import start_export, PLATFORM_PRESETS
from app.core.exceptions import ClipNotFoundError


class TestExportService:
    @pytest.mark.asyncio
    async def test_export_clip_not_found(self, mock_db_session):
        with patch("app.services.export_service.get_clip", return_value=None):
            with pytest.raises(ClipNotFoundError):
                await start_export(mock_db_session, uuid.uuid4(), "9:16")

    @pytest.mark.asyncio
    async def test_export_with_platform_preset(self, mock_db_session):
        mock_clip = MagicMock()
        mock_clip.id = uuid.uuid4()
        mock_clip.video_id = uuid.uuid4()

        mock_job = MagicMock()
        mock_job.id = uuid.uuid4()

        mock_export = MagicMock()
        mock_export.id = uuid.uuid4()

        with patch("app.services.export_service.get_clip", return_value=mock_clip), \
             patch("app.services.export_service.create_job", return_value=mock_job), \
             patch("app.services.export_service.create_export", return_value=mock_export), \
             patch("worker.tasks.export_tasks.export_clip.delay", side_effect=Exception("No celery")):
            result = await start_export(mock_db_session, mock_clip.id, "9:16", "tiktok")
            assert "job_id" in result
            assert "export_id" in result

    def test_platform_presets(self):
        assert "tiktok" in PLATFORM_PRESETS
        assert "instagram" in PLATFORM_PRESETS
        assert PLATFORM_PRESETS["tiktok"]["width"] == 1080
        assert PLATFORM_PRESETS["tiktok"]["height"] == 1920
