"""Periodic cleanup tasks."""
import os
import time
from pathlib import Path
from worker.app import celery_app
import structlog

logger = structlog.get_logger(__name__)

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/app/uploads")


@celery_app.task(name="worker.tasks.cleanup_tasks.cleanup_temp_files")
def cleanup_temp_files():
    """Remove stale upload chunks older than 24 hours."""
    chunks_dir = Path(UPLOAD_DIR) / "chunks"
    if not chunks_dir.exists():
        return {"cleaned": 0}

    cutoff = time.time() - 86400  # 24 hours ago
    cleaned = 0

    for chunk_dir in chunks_dir.iterdir():
        if chunk_dir.is_dir():
            try:
                dir_mtime = chunk_dir.stat().st_mtime
                if dir_mtime < cutoff:
                    import shutil
                    shutil.rmtree(chunk_dir)
                    cleaned += 1
                    logger.info("stale_chunks_cleaned", directory=str(chunk_dir))
            except Exception as e:
                logger.warning("cleanup_failed", directory=str(chunk_dir), error=str(e))

    logger.info("cleanup_completed", cleaned=cleaned)
    return {"cleaned": cleaned}
