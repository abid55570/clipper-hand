"""Unit tests for configuration."""
from app.config import Settings


class TestSettings:
    def test_default_settings(self):
        s = Settings()
        assert s.app_port == 8000
        assert s.max_upload_size_gb == 10.0
        assert s.chunk_size_mb == 5

    def test_cors_origin_list(self):
        s = Settings(cors_origins="http://localhost:3000,http://localhost:5173")
        origins = s.cors_origin_list
        assert len(origins) == 2
        assert "http://localhost:3000" in origins
        assert "http://localhost:5173" in origins

    def test_max_upload_size_bytes(self):
        s = Settings(max_upload_size_gb=1.0)
        assert s.max_upload_size_bytes == 1 * 1024 * 1024 * 1024

    def test_chunk_size_bytes(self):
        s = Settings(chunk_size_mb=10)
        assert s.chunk_size_bytes == 10 * 1024 * 1024
