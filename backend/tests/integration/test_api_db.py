"""Integration tests for API endpoints with database interactions."""
import uuid
import pytest
from unittest.mock import patch, MagicMock


class TestVideoEndpoints:
    def test_get_video_not_found(self, test_client):
        client, mock_session = test_client
        video_id = uuid.uuid4()
        with patch("app.api.v1.videos.get_video", return_value=None):
            response = client.get(f"/api/v1/videos/{video_id}")
            assert response.status_code == 404

    def test_delete_video_not_found(self, test_client):
        client, mock_session = test_client
        video_id = uuid.uuid4()
        with patch("app.api.v1.videos.get_video", return_value=None):
            response = client.delete(f"/api/v1/videos/{video_id}")
            assert response.status_code == 404


class TestClipEndpoints:
    def test_get_clip_not_found(self, test_client):
        client, mock_session = test_client
        clip_id = uuid.uuid4()
        with patch("app.api.v1.clips.get_clip", return_value=None):
            response = client.get(f"/api/v1/clips/{clip_id}")
            assert response.status_code == 404


class TestJobEndpoints:
    def test_get_job_not_found(self, test_client):
        client, mock_session = test_client
        job_id = uuid.uuid4()
        with patch("app.api.v1.jobs.get_job", return_value=None):
            response = client.get(f"/api/v1/jobs/{job_id}")
            assert response.status_code == 404
