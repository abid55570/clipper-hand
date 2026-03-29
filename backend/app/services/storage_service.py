import os
import uuid
import shutil
from pathlib import Path
from app.config import settings
from app.core.logging import get_logger
from app.core.security import sanitize_filename

logger = get_logger(__name__)


class StorageService:
    """Local filesystem storage with chunk upload support.
    Designed to be swappable with S3 implementation later.
    """

    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.media_dir = Path(settings.media_dir)
        self.chunk_dir = self.upload_dir / "chunks"

    def _ensure_dirs(self):
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.media_dir.mkdir(parents=True, exist_ok=True)
        self.chunk_dir.mkdir(parents=True, exist_ok=True)

    def init_upload(self, upload_id: str) -> Path:
        """Create a directory for upload chunks."""
        self._ensure_dirs()
        chunk_path = self.chunk_dir / upload_id
        chunk_path.mkdir(parents=True, exist_ok=True)
        return chunk_path

    async def save_chunk(self, upload_id: str, chunk_index: int, data: bytes) -> Path:
        """Save a single chunk to disk."""
        chunk_path = self.chunk_dir / upload_id
        chunk_path.mkdir(parents=True, exist_ok=True)
        chunk_file = chunk_path / f"chunk_{chunk_index:06d}"
        chunk_file.write_bytes(data)
        logger.debug("chunk_saved", upload_id=upload_id, chunk_index=chunk_index, size=len(data))
        return chunk_file

    async def assemble_chunks(self, upload_id: str, filename: str) -> Path:
        """Assemble all chunks into a single file."""
        self._ensure_dirs()
        chunk_path = self.chunk_dir / upload_id
        safe_name = sanitize_filename(filename)
        unique_name = f"{uuid.uuid4().hex[:12]}_{safe_name}"
        output_path = self.upload_dir / unique_name

        # Get sorted chunk files
        chunks = sorted(chunk_path.glob("chunk_*"))
        if not chunks:
            raise FileNotFoundError(f"No chunks found for upload {upload_id}")

        # Assemble chunks
        with open(output_path, "wb") as outfile:
            for chunk_file in chunks:
                outfile.write(chunk_file.read_bytes())

        # Clean up chunks
        shutil.rmtree(chunk_path, ignore_errors=True)

        logger.info("chunks_assembled", upload_id=upload_id, output=str(output_path), size=output_path.stat().st_size)
        return output_path

    def get_clip_output_path(self, video_filename: str, label: str | None = None) -> Path:
        """Generate a unique output path for a clip."""
        self._ensure_dirs()
        base = Path(video_filename).stem
        clip_name = f"{base}_{label or 'clip'}_{uuid.uuid4().hex[:8]}.mp4"
        return self.media_dir / clip_name

    def get_export_output_path(self, clip_filename: str, aspect_ratio: str) -> Path:
        """Generate a unique output path for an export."""
        self._ensure_dirs()
        base = Path(clip_filename).stem
        ratio_str = aspect_ratio.replace(":", "x")
        export_name = f"{base}_export_{ratio_str}_{uuid.uuid4().hex[:8]}.mp4"
        return self.media_dir / export_name

    def get_path(self, file_path: str) -> Path:
        """Get a Path object for a stored file."""
        return Path(file_path)

    def file_exists(self, file_path: str) -> bool:
        """Check if a file exists."""
        return Path(file_path).exists()

    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes."""
        return Path(file_path).stat().st_size

    def delete(self, file_path: str) -> bool:
        """Delete a file."""
        try:
            Path(file_path).unlink(missing_ok=True)
            return True
        except Exception as e:
            logger.error("file_delete_failed", path=file_path, error=str(e))
            return False


# Singleton instance
storage = StorageService()
