import uuid
import json
import subprocess
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.crud.video import create_video, get_video, update_video
from app.db.crud.job import create_job
from app.services.storage_service import storage
from app.core.security import validate_video_extension, validate_file_size, validate_video_magic_bytes
from app.core.exceptions import VideoNotFoundError, UploadNotFoundError
from app.core.logging import get_logger
from app.config import settings

logger = get_logger(__name__)

# In-memory upload session tracker (use Redis in production for multi-process)
_upload_sessions: dict[str, dict] = {}


async def init_upload(session: AsyncSession, filename: str, file_size: int, content_type: str) -> dict:
    """Initialize a chunked upload session."""
    validate_video_extension(filename)
    validate_file_size(file_size)

    upload_id = uuid.uuid4().hex
    chunk_size = settings.chunk_size_bytes
    total_chunks = (file_size + chunk_size - 1) // chunk_size

    storage.init_upload(upload_id)

    _upload_sessions[upload_id] = {
        "filename": filename,
        "file_size": file_size,
        "content_type": content_type,
        "total_chunks": total_chunks,
        "received_chunks": set(),
    }

    logger.info("upload_initialized", upload_id=upload_id, filename=filename, total_chunks=total_chunks)
    return {"upload_id": upload_id, "chunk_size": chunk_size, "total_chunks": total_chunks}


async def save_upload_chunk(upload_id: str, chunk_index: int, data: bytes) -> dict:
    """Save a chunk of an upload."""
    if upload_id not in _upload_sessions:
        raise UploadNotFoundError(upload_id)

    session_info = _upload_sessions[upload_id]

    # Validate first chunk's magic bytes
    if chunk_index == 0:
        validate_video_magic_bytes(data[:12])

    await storage.save_chunk(upload_id, chunk_index, data)
    session_info["received_chunks"].add(chunk_index)

    return {"chunk_index": chunk_index, "received": True}


async def complete_upload(session: AsyncSession, upload_id: str) -> dict:
    """Finalize upload: assemble chunks, create video record, dispatch metadata extraction."""
    if upload_id not in _upload_sessions:
        raise UploadNotFoundError(upload_id)

    session_info = _upload_sessions[upload_id]

    # Assemble chunks
    file_path = await storage.assemble_chunks(upload_id, session_info["filename"])
    file_size = storage.get_file_size(str(file_path))

    # Create video record
    video = await create_video(
        session,
        filename=file_path.name,
        original_name=session_info["filename"],
        file_path=str(file_path),
        file_size_bytes=file_size,
        status="processing",
    )

    # Create job for metadata extraction
    job = await create_job(
        session,
        job_type="metadata_extract",
        video_id=video.id,
        status="pending",
    )

    # Clean up upload session
    del _upload_sessions[upload_id]

    # Dispatch Celery task for metadata extraction
    try:
        from worker.tasks.clip_tasks import extract_metadata
        task = extract_metadata.delay(str(job.id), str(video.id))
        job.celery_task_id = task.id
        await session.flush()
    except Exception as e:
        logger.warning("celery_dispatch_failed", error=str(e), job_id=str(job.id))

    logger.info("upload_completed", video_id=str(video.id), file_path=str(file_path))
    return {"video_id": video.id, "job_id": job.id}


def extract_video_metadata(file_path: str) -> dict:
    """Extract video metadata using ffprobe (sync, for workers)."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                str(file_path),
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        probe_data = json.loads(result.stdout)

        # Find video stream
        video_stream = None
        for stream in probe_data.get("streams", []):
            if stream.get("codec_type") == "video":
                video_stream = stream
                break

        metadata = {
            "duration_secs": float(probe_data.get("format", {}).get("duration", 0)),
        }

        if video_stream:
            metadata["width"] = int(video_stream.get("width", 0))
            metadata["height"] = int(video_stream.get("height", 0))
            metadata["codec"] = video_stream.get("codec_name", "unknown")
            # Parse fps from r_frame_rate (e.g., "30/1")
            fps_str = video_stream.get("r_frame_rate", "0/1")
            if "/" in fps_str:
                num, den = fps_str.split("/")
                metadata["fps"] = float(num) / float(den) if float(den) != 0 else 0
            else:
                metadata["fps"] = float(fps_str)

        return metadata
    except Exception as e:
        logger.error("metadata_extraction_failed", file_path=file_path, error=str(e))
        return {}
