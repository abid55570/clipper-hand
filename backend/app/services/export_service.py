import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.crud.clip import get_clip
from app.db.crud.export import create_export
from app.db.crud.job import create_job
from app.core.exceptions import ClipNotFoundError
from app.core.logging import get_logger

logger = get_logger(__name__)

# Platform presets
PLATFORM_PRESETS = {
    "tiktok": {"aspect_ratio": "9:16", "width": 1080, "height": 1920},
    "instagram": {"aspect_ratio": "9:16", "width": 1080, "height": 1920},
    "youtube_shorts": {"aspect_ratio": "9:16", "width": 1080, "height": 1920},
    "twitter": {"aspect_ratio": "16:9", "width": 1920, "height": 1080},
}

ASPECT_RATIO_DIMENSIONS = {
    "16:9": (1920, 1080),
    "9:16": (1080, 1920),
    "1:1": (1080, 1080),
    "4:5": (1080, 1350),
}


async def start_export(
    session: AsyncSession,
    clip_id: uuid.UUID,
    aspect_ratio: str,
    platform: str | None = None,
    effects: dict | None = None,
) -> dict:
    """Start an export job for a clip."""
    clip = await get_clip(session, clip_id)
    if not clip:
        raise ClipNotFoundError(str(clip_id))

    # Determine dimensions
    if platform and platform in PLATFORM_PRESETS:
        preset = PLATFORM_PRESETS[platform]
        width, height = preset["width"], preset["height"]
    else:
        width, height = ASPECT_RATIO_DIMENSIONS.get(aspect_ratio, (1920, 1080))

    job = await create_job(
        session,
        job_type="export",
        clip_id=clip_id,
        video_id=clip.video_id,
        status="pending",
    )

    export = await create_export(
        session,
        clip_id=clip_id,
        job_id=job.id,
        aspect_ratio=aspect_ratio,
        platform=platform,
        width=width,
        height=height,
        effects_json=effects,
        status="pending",
    )

    try:
        from worker.tasks.export_tasks import export_clip
        task = export_clip.delay(
            str(job.id), str(export.id), str(clip_id),
            aspect_ratio, width, height, effects,
        )
        job.celery_task_id = task.id
        await session.flush()
    except Exception as e:
        logger.warning("celery_dispatch_failed", error=str(e))

    return {"job_id": job.id, "export_id": export.id}
