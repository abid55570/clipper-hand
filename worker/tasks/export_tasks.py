"""Celery tasks for video export with resize, crop, and effects."""
import os
import uuid
from celery.exceptions import SoftTimeLimitExceeded
from worker.app import celery_app
from worker.processors import ffmpeg_wrapper
from worker.processors.smart_crop import smart_crop_video
from worker.processors.effects import apply_effects_chain
import structlog

logger = structlog.get_logger(__name__)

MEDIA_DIR = os.environ.get("MEDIA_DIR", "/app/media")


def _get_db_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine(
        os.environ.get("DATABASE_URL_SYNC", "postgresql://clipper:clipper_pass@postgres:5432/clipper_db"),
        pool_pre_ping=True,
    )
    return sessionmaker(bind=engine)()


def _update_job(session, job_id: str, **kwargs):
    from app.models.job import Job
    job = session.query(Job).filter(Job.id == uuid.UUID(job_id)).first()
    if job:
        for k, v in kwargs.items():
            setattr(job, k, v)
        session.commit()


@celery_app.task(bind=True, name="worker.tasks.export_tasks.export_clip",
                 max_retries=2, default_retry_delay=60)
def export_clip(self, job_id: str, export_id: str, clip_id: str,
                 aspect_ratio: str, width: int, height: int,
                 effects_config: dict | None = None):
    """Export a clip with resize, crop, and optional effects."""
    session = _get_db_session()
    try:
        _update_job(session, job_id, status="running", progress_pct=5)

        from app.models.clip import Clip
        from app.models.export import Export

        clip = session.query(Clip).filter(Clip.id == uuid.UUID(clip_id)).first()
        if not clip or not clip.file_path:
            _update_job(session, job_id, status="failed", error_message="Clip not found or not ready")
            return

        export = session.query(Export).filter(Export.id == uuid.UUID(export_id)).first()
        if not export:
            _update_job(session, job_id, status="failed", error_message="Export not found")
            return

        os.makedirs(MEDIA_DIR, exist_ok=True)
        ratio_str = aspect_ratio.replace(":", "x")
        output_path = os.path.join(MEDIA_DIR, f"{uuid.uuid4().hex[:8]}_export_{ratio_str}.mp4")

        # Step 1: Smart crop and resize
        _update_job(session, job_id, progress_pct=20)
        resized_path = output_path + ".resized.mp4"
        smart_crop_video(clip.file_path, resized_path, width, height)
        _update_job(session, job_id, progress_pct=60)

        # Step 2: Apply effects if requested
        if effects_config:
            apply_effects_chain(resized_path, output_path, effects_config)
            os.unlink(resized_path)
        else:
            os.rename(resized_path, output_path)

        _update_job(session, job_id, progress_pct=90)

        # Update export record
        file_size = os.path.getsize(output_path)
        export.file_path = output_path
        export.file_size_bytes = file_size
        export.status = "ready"
        session.commit()

        _update_job(session, job_id, status="completed", progress_pct=100,
                    result_json={"file_path": output_path, "file_size": file_size})
        logger.info("export_completed", export_id=export_id, output=output_path)

    except SoftTimeLimitExceeded:
        _update_job(session, job_id, status="failed", error_message="Export timed out")
    except Exception as exc:
        _update_job(session, job_id, status="failed", error_message=str(exc))
        raise self.retry(exc=exc)
    finally:
        session.close()
