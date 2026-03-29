"""Celery tasks for video clip extraction, trimming, merging, and batch processing."""
import os
import uuid
from celery import chord
from celery.exceptions import SoftTimeLimitExceeded
from worker.app import celery_app
from worker.processors import ffmpeg_wrapper
import structlog

logger = structlog.get_logger(__name__)

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/app/uploads")
MEDIA_DIR = os.environ.get("MEDIA_DIR", "/app/media")


def _get_db_session():
    """Get a sync DB session for workers."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine(
        os.environ.get("DATABASE_URL_SYNC", "postgresql://clipper:clipper_pass@postgres:5432/clipper_db"),
        pool_pre_ping=True,
    )
    Session = sessionmaker(bind=engine)
    return Session()


def _update_job(session, job_id: str, **kwargs):
    from app.models.job import Job
    job = session.query(Job).filter(Job.id == uuid.UUID(job_id)).first()
    if job:
        for k, v in kwargs.items():
            setattr(job, k, v)
        session.commit()


def _update_clip(session, clip_id: str, **kwargs):
    from app.models.clip import Clip
    clip = session.query(Clip).filter(Clip.id == uuid.UUID(clip_id)).first()
    if clip:
        for k, v in kwargs.items():
            setattr(clip, k, v)
        session.commit()


def _get_video(session, video_id: str):
    from app.models.video import Video
    return session.query(Video).filter(Video.id == uuid.UUID(video_id)).first()


@celery_app.task(bind=True, name="worker.tasks.clip_tasks.extract_metadata",
                 max_retries=3, default_retry_delay=30)
def extract_metadata(self, job_id: str, video_id: str):
    """Extract video metadata using ffprobe."""
    session = _get_db_session()
    try:
        _update_job(session, job_id, status="running", progress_pct=10)
        video = _get_video(session, video_id)
        if not video:
            _update_job(session, job_id, status="failed", error_message="Video not found")
            return

        metadata = ffmpeg_wrapper.probe(video.file_path)
        video_stream = next(
            (s for s in metadata.get("streams", []) if s.get("codec_type") == "video"), None
        )

        update_data = {
            "duration_secs": float(metadata.get("format", {}).get("duration", 0)),
            "status": "ready",
        }
        if video_stream:
            update_data["width"] = int(video_stream.get("width", 0))
            update_data["height"] = int(video_stream.get("height", 0))
            update_data["codec"] = video_stream.get("codec_name", "unknown")
            fps_str = video_stream.get("r_frame_rate", "0/1")
            if "/" in fps_str:
                num, den = fps_str.split("/")
                update_data["fps"] = float(num) / float(den) if float(den) != 0 else 0
            else:
                update_data["fps"] = float(fps_str)

        from app.models.video import Video
        v = session.query(Video).filter(Video.id == uuid.UUID(video_id)).first()
        if v:
            for k, val in update_data.items():
                setattr(v, k, val)
            session.commit()

        _update_job(session, job_id, status="completed", progress_pct=100,
                    result_json={"duration": update_data.get("duration_secs")})
        logger.info("metadata_extracted", video_id=video_id)

    except SoftTimeLimitExceeded:
        _update_job(session, job_id, status="failed", error_message="Task timed out")
    except Exception as exc:
        _update_job(session, job_id, status="failed", error_message=str(exc))
        raise self.retry(exc=exc)
    finally:
        session.close()


@celery_app.task(bind=True, name="worker.tasks.clip_tasks.extract_single_clip",
                 max_retries=3, default_retry_delay=60)
def extract_single_clip(self, job_id: str, video_id: str, clip_id: str,
                         start: float, end: float, label: str = "clip"):
    """Extract a single clip from a video."""
    session = _get_db_session()
    try:
        _update_clip(session, clip_id, status="processing")
        video = _get_video(session, video_id)
        if not video:
            _update_clip(session, clip_id, status="error")
            return

        os.makedirs(MEDIA_DIR, exist_ok=True)
        safe_label = label.replace(" ", "_")[:50] if label else "clip"
        output_filename = f"{uuid.uuid4().hex[:8]}_{safe_label}.mp4"
        output_path = os.path.join(MEDIA_DIR, output_filename)

        ffmpeg_wrapper.extract_segment(video.file_path, start, end, output_path)

        file_size = os.path.getsize(output_path)
        _update_clip(session, clip_id,
                     file_path=output_path,
                     file_size_bytes=file_size,
                     status="ready")

        logger.info("clip_extracted", clip_id=clip_id, output=output_path)
        return {"clip_id": clip_id, "file_path": output_path}

    except SoftTimeLimitExceeded:
        _update_clip(session, clip_id, status="error")
    except Exception as exc:
        _update_clip(session, clip_id, status="error")
        raise self.retry(exc=exc)
    finally:
        session.close()


@celery_app.task(bind=True, name="worker.tasks.clip_tasks.batch_extract_clips",
                 max_retries=2, default_retry_delay=60)
def batch_extract_clips(self, job_id: str, video_id: str, clips_data: list[dict]):
    """Batch extract multiple clips from a video."""
    session = _get_db_session()
    try:
        _update_job(session, job_id, status="running", progress_pct=0)

        total = len(clips_data)
        for i, clip_info in enumerate(clips_data):
            extract_single_clip(
                job_id, video_id,
                clip_info["clip_id"],
                clip_info["start"],
                clip_info["end"],
                clip_info.get("label", f"clip_{i+1}"),
            )
            progress = int(((i + 1) / total) * 100)
            _update_job(session, job_id, progress_pct=progress)

        _update_job(session, job_id, status="completed", progress_pct=100,
                    result_json={"clips_processed": total})
        logger.info("batch_extract_completed", job_id=job_id, total=total)

    except SoftTimeLimitExceeded:
        _update_job(session, job_id, status="failed", error_message="Batch task timed out")
    except Exception as exc:
        _update_job(session, job_id, status="failed", error_message=str(exc))
        raise self.retry(exc=exc)
    finally:
        session.close()


@celery_app.task(bind=True, name="worker.tasks.clip_tasks.trim_clip_task",
                 max_retries=3, default_retry_delay=60)
def trim_clip_task(self, job_id: str, video_id: str, clip_id: str,
                    start: float, end: float):
    """Trim a clip to new timestamps."""
    session = _get_db_session()
    try:
        _update_job(session, job_id, status="running", progress_pct=10)
        video = _get_video(session, video_id)
        if not video:
            _update_job(session, job_id, status="failed", error_message="Video not found")
            return

        os.makedirs(MEDIA_DIR, exist_ok=True)
        output_path = os.path.join(MEDIA_DIR, f"{uuid.uuid4().hex[:8]}_trimmed.mp4")

        ffmpeg_wrapper.extract_segment(video.file_path, start, end, output_path)

        file_size = os.path.getsize(output_path)
        _update_clip(session, clip_id,
                     file_path=output_path,
                     file_size_bytes=file_size,
                     duration_secs=end - start,
                     status="ready")

        _update_job(session, job_id, status="completed", progress_pct=100)
        logger.info("clip_trimmed", clip_id=clip_id)

    except Exception as exc:
        _update_job(session, job_id, status="failed", error_message=str(exc))
        raise self.retry(exc=exc)
    finally:
        session.close()


@celery_app.task(bind=True, name="worker.tasks.clip_tasks.merge_clips_task",
                 max_retries=2, default_retry_delay=60)
def merge_clips_task(self, job_id: str, clip_ids: list[str], merged_clip_id: str):
    """Merge multiple clips into one."""
    session = _get_db_session()
    try:
        _update_job(session, job_id, status="running", progress_pct=10)

        from app.models.clip import Clip
        input_paths = []
        for cid in clip_ids:
            clip = session.query(Clip).filter(Clip.id == uuid.UUID(cid)).first()
            if clip and clip.file_path:
                input_paths.append(clip.file_path)

        if len(input_paths) < 2:
            _update_job(session, job_id, status="failed",
                        error_message="Need at least 2 ready clips to merge")
            return

        os.makedirs(MEDIA_DIR, exist_ok=True)
        output_path = os.path.join(MEDIA_DIR, f"{uuid.uuid4().hex[:8]}_merged.mp4")

        ffmpeg_wrapper.merge_segments(input_paths, output_path)

        file_size = os.path.getsize(output_path)
        _update_clip(session, merged_clip_id,
                     file_path=output_path,
                     file_size_bytes=file_size,
                     status="ready")

        _update_job(session, job_id, status="completed", progress_pct=100)
        logger.info("clips_merged", merged_clip_id=merged_clip_id)

    except Exception as exc:
        _update_job(session, job_id, status="failed", error_message=str(exc))
        raise self.retry(exc=exc)
    finally:
        session.close()
