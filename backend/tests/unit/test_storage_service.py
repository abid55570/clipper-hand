"""Unit tests for storage service."""
import os
import uuid
import pytest
from pathlib import Path
from app.services.storage_service import StorageService


class TestStorageService:
    @pytest.fixture
    def storage(self, tmp_path):
        svc = StorageService()
        svc.upload_dir = tmp_path / "uploads"
        svc.media_dir = tmp_path / "media"
        svc.chunk_dir = svc.upload_dir / "chunks"
        return svc

    def test_init_upload_creates_directory(self, storage):
        upload_id = "test_upload_123"
        path = storage.init_upload(upload_id)
        assert path.exists()
        assert path.is_dir()

    @pytest.mark.asyncio
    async def test_save_chunk(self, storage):
        upload_id = "test_upload_456"
        data = b"chunk data here"
        path = await storage.save_chunk(upload_id, 0, data)
        assert path.exists()
        assert path.read_bytes() == data

    @pytest.mark.asyncio
    async def test_save_multiple_chunks(self, storage):
        upload_id = "test_multi"
        await storage.save_chunk(upload_id, 0, b"chunk0")
        await storage.save_chunk(upload_id, 1, b"chunk1")
        await storage.save_chunk(upload_id, 2, b"chunk2")

        chunk_dir = storage.chunk_dir / upload_id
        assert len(list(chunk_dir.glob("chunk_*"))) == 3

    @pytest.mark.asyncio
    async def test_assemble_chunks(self, storage):
        upload_id = "test_assemble"
        await storage.save_chunk(upload_id, 0, b"hello ")
        await storage.save_chunk(upload_id, 1, b"world")

        output = await storage.assemble_chunks(upload_id, "test.mp4")
        assert output.exists()
        assert output.read_bytes() == b"hello world"

        # Chunks should be cleaned up
        chunk_dir = storage.chunk_dir / upload_id
        assert not chunk_dir.exists()

    @pytest.mark.asyncio
    async def test_assemble_chunks_no_chunks(self, storage):
        upload_id = "empty_upload"
        storage.init_upload(upload_id)
        with pytest.raises(FileNotFoundError):
            await storage.assemble_chunks(upload_id, "test.mp4")

    def test_get_clip_output_path(self, storage):
        path = storage.get_clip_output_path("video.mp4", "intro")
        assert str(path).endswith(".mp4")
        assert "intro" in str(path)

    def test_get_export_output_path(self, storage):
        path = storage.get_export_output_path("clip.mp4", "9:16")
        assert "9x16" in str(path)
        assert str(path).endswith(".mp4")

    def test_file_exists(self, storage, tmp_path):
        test_file = tmp_path / "exists.txt"
        test_file.write_text("hello")
        assert storage.file_exists(str(test_file))
        assert not storage.file_exists(str(tmp_path / "nope.txt"))

    def test_get_file_size(self, storage, tmp_path):
        test_file = tmp_path / "sized.txt"
        test_file.write_bytes(b"12345")
        assert storage.get_file_size(str(test_file)) == 5

    def test_delete_file(self, storage, tmp_path):
        test_file = tmp_path / "deleteme.txt"
        test_file.write_text("bye")
        assert storage.delete(str(test_file))
        assert not test_file.exists()

    def test_delete_nonexistent(self, storage):
        assert storage.delete("/nonexistent/file.txt")
