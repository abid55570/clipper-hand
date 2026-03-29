import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.crud.video import get_video
from app.db.crud.clip import get_clip
from app.db.crud.job import create_job
from app.core.exceptions import VideoNotFoundError, ClipNotFoundError
from app.core.logging import get_logger

logger = get_logger(__name__)


async def start_highlight_detection(session: AsyncSession, video_id: uuid.UUID) -> dict:
    """Start AI highlight detection for a video."""
    video = await get_video(session, video_id)
    if not video:
        raise VideoNotFoundError(str(video_id))

    job = await create_job(
        session,
        job_type="detect_highlights",
        video_id=video_id,
        status="pending",
    )

    try:
        from worker.tasks.ai_tasks import detect_highlights
        task = detect_highlights.delay(str(job.id), str(video_id))
        job.celery_task_id = task.id
        await session.flush()
    except Exception as e:
        logger.warning("celery_dispatch_failed", error=str(e))

    return {"job_id": job.id}


async def start_content_generation(session: AsyncSession, clip_id: uuid.UUID) -> dict:
    """Generate title, description, hashtags for a clip."""
    clip = await get_clip(session, clip_id)
    if not clip:
        raise ClipNotFoundError(str(clip_id))

    job = await create_job(
        session,
        job_type="generate_content",
        clip_id=clip_id,
        video_id=clip.video_id,
        status="pending",
    )

    try:
        from worker.tasks.ai_tasks import generate_content
        task = generate_content.delay(str(job.id), str(clip_id))
        job.celery_task_id = task.id
        await session.flush()
    except Exception as e:
        logger.warning("celery_dispatch_failed", error=str(e))

    return {"job_id": job.id}


async def start_hook_generation(session: AsyncSession, clip_id: uuid.UUID) -> dict:
    """Generate hook text for a clip."""
    clip = await get_clip(session, clip_id)
    if not clip:
        raise ClipNotFoundError(str(clip_id))

    job = await create_job(
        session,
        job_type="generate_hook",
        clip_id=clip_id,
        video_id=clip.video_id,
        status="pending",
    )

    try:
        from worker.tasks.ai_tasks import generate_hooks
        task = generate_hooks.delay(str(job.id), str(clip_id))
        job.celery_task_id = task.id
        await session.flush()
    except Exception as e:
        logger.warning("celery_dispatch_failed", error=str(e))

    return {"job_id": job.id}


async def start_speaker_detection(session: AsyncSession, video_id: uuid.UUID) -> dict:
    """Start speaker detection (placeholder)."""
    video = await get_video(session, video_id)
    if not video:
        raise VideoNotFoundError(str(video_id))

    job = await create_job(
        session,
        job_type="detect_speakers",
        video_id=video_id,
        status="pending",
    )

    try:
        from worker.tasks.ai_tasks import detect_speakers
        task = detect_speakers.delay(str(job.id), str(video_id))
        job.celery_task_id = task.id
        await session.flush()
    except Exception as e:
        logger.warning("celery_dispatch_failed", error=str(e))

    return {"job_id": job.id}
