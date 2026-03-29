import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.crud.caption import create_caption, create_or_update_caption_style
from app.db.crud.video import get_video
from app.db.crud.job import create_job
from app.core.exceptions import VideoNotFoundError, ClipNotFoundError
from app.core.logging import get_logger

logger = get_logger(__name__)


async def start_transcription(
    session: AsyncSession, video_id: uuid.UUID, model_size: str = "base"
) -> dict:
    """Start a transcription job for a video."""
    video = await get_video(session, video_id)
    if not video:
        raise VideoNotFoundError(str(video_id))

    caption = await create_caption(
        session,
        video_id=video_id,
        model_size=model_size,
        status="pending",
    )

    job = await create_job(
        session,
        job_type="transcribe",
        video_id=video_id,
        status="pending",
    )

    try:
        from worker.tasks.caption_tasks import transcribe_video
        task = transcribe_video.delay(str(job.id), str(video_id), str(caption.id), model_size)
        job.celery_task_id = task.id
        await session.flush()
    except Exception as e:
        logger.warning("celery_dispatch_failed", error=str(e))

    return {"job_id": job.id, "caption_id": caption.id}


async def update_caption_style(
    session: AsyncSession, caption_id: uuid.UUID, style_data: dict
) -> dict:
    """Update caption styling."""
    style = await create_or_update_caption_style(session, caption_id, **style_data)
    return {"style_id": style.id}


async def start_burn_subtitles(
    session: AsyncSession, clip_id: uuid.UUID, caption_id: uuid.UUID, style_data: dict | None = None
) -> dict:
    """Burn subtitles into a clip."""
    from app.db.crud.clip import get_clip
    clip = await get_clip(session, clip_id)
    if not clip:
        raise ClipNotFoundError(str(clip_id))

    job = await create_job(
        session,
        job_type="burn_subtitles",
        clip_id=clip_id,
        video_id=clip.video_id,
        status="pending",
    )

    try:
        from worker.tasks.caption_tasks import burn_subtitles
        task = burn_subtitles.delay(str(job.id), str(clip_id), str(caption_id), style_data)
        job.celery_task_id = task.id
        await session.flush()
    except Exception as e:
        logger.warning("celery_dispatch_failed", error=str(e))

    return {"job_id": job.id}
