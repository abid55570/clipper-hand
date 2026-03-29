"""Integration tests for upload → process → download flow."""
import io
import pytest
from unittest.mock import patch, MagicMock, AsyncMock


class TestUploadFlow:
    def test_health_check(self, test_client):
        client, _ = test_client
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_upload_init_success(self, test_client):
        client, mock_session = test_client
        with patch("app.services.video_service.init_upload") as mock_init:
            mock_init.return_value = {
                "upload_id": "abc123",
                "chunk_size": 5242880,
                "total_chunks": 1,
            }
            response = client.post("/api/v1/videos/upload/init", json={
                "filename": "test_video.mp4",
                "file_size": 1024000,
                "content_type": "video/mp4",
            })
            assert response.status_code == 200
            data = response.json()
            assert data["upload_id"] == "abc123"
            assert data["total_chunks"] == 1

    def test_upload_init_invalid_extension(self, test_client):
        client, _ = test_client
        response = client.post("/api/v1/videos/upload/init", json={
            "filename": "test.txt",
            "file_size": 1024,
            "content_type": "text/plain",
        })
        assert response.status_code == 400

    def test_list_videos(self, test_client):
        client, mock_session = test_client
        with patch("app.api.v1.videos.list_videos", return_value=[]):
            response = client.get("/api/v1/videos")
            assert response.status_code == 200
            data = response.json()
            assert "videos" in data


class TestClipFlow:
    def test_list_clips(self, test_client):
        client, mock_session = test_client
        with patch("app.api.v1.clips.list_clips", return_value=[]):
            response = client.get("/api/v1/clips")
            assert response.status_code == 200
            data = response.json()
            assert "clips" in data


class TestJobFlow:
    def test_list_jobs(self, test_client):
        client, mock_session = test_client
        with patch("app.api.v1.jobs.list_jobs", return_value=[]):
            response = client.get("/api/v1/jobs")
            assert response.status_code == 200
            data = response.json()
            assert "jobs" in data
