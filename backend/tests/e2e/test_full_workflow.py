"""End-to-end tests for the full video clipping workflow."""
import uuid
import pytest
from unittest.mock import patch, MagicMock, AsyncMock


class TestFullWorkflow:
    """E2E test: Upload video → Add timestamps → Generate clip → Download result."""

    def test_full_clip_workflow(self, test_client):
        """Test the complete clip creation workflow."""
        client, mock_session = test_client

        # Step 1: Init upload
        with patch("app.services.video_service.init_upload") as mock_init:
            mock_init.return_value = {
                "upload_id": "test_upload_123",
                "chunk_size": 5242880,
                "total_chunks": 1,
            }
            response = client.post("/api/v1/videos/upload/init", json={
                "filename": "test_video.mp4",
                "file_size": 1024000,
                "content_type": "video/mp4",
            })
            assert response.status_code == 200
            upload_data = response.json()
            assert upload_data["upload_id"] == "test_upload_123"

        # Step 2: Complete upload
        video_id = uuid.uuid4()
        job_id = uuid.uuid4()
        with patch("app.services.video_service.complete_upload") as mock_complete:
            mock_complete.return_value = {
                "video_id": video_id,
                "job_id": job_id,
            }
            response = client.post("/api/v1/videos/upload/complete/test_upload_123")
            assert response.status_code == 200
            complete_data = response.json()
            assert "video_id" in complete_data

        # Step 3: Get video details
        mock_video = MagicMock()
        mock_video.id = video_id
        mock_video.filename = "test_video.mp4"
        mock_video.original_name = "test_video.mp4"
        mock_video.file_size_bytes = 1024000
        mock_video.duration_secs = 120.0
        mock_video.width = 1920
        mock_video.height = 1080
        mock_video.fps = 30.0
        mock_video.codec = "h264"
        mock_video.status = "ready"
        mock_video.created_at = "2024-01-01T00:00:00Z"
        mock_video.updated_at = "2024-01-01T00:00:00Z"

        with patch("app.api.v1.videos.get_video", return_value=mock_video):
            response = client.get(f"/api/v1/videos/{video_id}")
            assert response.status_code == 200
            video_data = response.json()
            assert video_data["status"] == "ready"
            assert video_data["duration_secs"] == 120.0

        # Step 4: Create clips with timestamps
        clip_job_id = uuid.uuid4()
        clip_ids = [uuid.uuid4(), uuid.uuid4()]
        with patch("app.services.clip_service.create_clips_from_timestamps") as mock_create:
            mock_create.return_value = {
                "job_id": clip_job_id,
                "clip_ids": clip_ids,
            }
            response = client.post(f"/api/v1/clips/video/{video_id}", json={
                "clips": [
                    {"start": 10.0, "end": 30.0, "label": "intro"},
                    {"start": 60.0, "end": 90.0, "label": "highlight"},
                ]
            })
            assert response.status_code == 200
            clips_data = response.json()
            assert len(clips_data["clip_ids"]) == 2

        # Step 5: Check job status
        mock_job = MagicMock()
        mock_job.id = clip_job_id
        mock_job.celery_task_id = "celery-task-123"
        mock_job.job_type = "batch_clip_extract"
        mock_job.status = "completed"
        mock_job.progress_pct = 100
        mock_job.result_json = {"clips_processed": 2}
        mock_job.error_message = None
        mock_job.retry_count = 0
        mock_job.video_id = video_id
        mock_job.clip_id = None
        mock_job.created_at = "2024-01-01T00:00:00Z"
        mock_job.updated_at = "2024-01-01T00:00:00Z"

        with patch("app.api.v1.jobs.get_job", return_value=mock_job):
            response = client.get(f"/api/v1/jobs/{clip_job_id}")
            assert response.status_code == 200
            job_data = response.json()
            assert job_data["status"] == "completed"
            assert job_data["progress_pct"] == 100

    def test_schema_validation(self, test_client):
        """Test that invalid requests are properly rejected."""
        client, _ = test_client

        # Invalid timestamps (end <= start)
        response = client.post(f"/api/v1/clips/video/{uuid.uuid4()}", json={
            "clips": [{"start": 30.0, "end": 10.0, "label": "invalid"}]
        })
        assert response.status_code == 422  # Validation error

        # Empty clips list
        response = client.post(f"/api/v1/clips/video/{uuid.uuid4()}", json={
            "clips": []
        })
        assert response.status_code == 422

    def test_health_endpoint(self, test_client):
        client, _ = test_client
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy", "version": "1.0.0"}
