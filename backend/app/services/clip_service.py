import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.crud.clip import create_clip
from app.db.crud.video import get_video
from app.db.crud.job import create_job
from app.core.exceptions import VideoNotFoundError, InvalidTimestampError
from app.core.logging import get_logger

logger = get_logger(__name__)


async def create_clips_from_timestamps(
    session: AsyncSession, video_id: uuid.UUID, clips_data: list[dict]
) -> dict:
    """Create clip records and dispatch extraction tasks."""
    video = await get_video(session, video_id)
    if not video:
        raise VideoNotFoundError(str(video_id))

    # Validate timestamps against video duration
    if video.duration_secs:
        for clip_data in clips_data:
            if clip_data["end"] > video.duration_secs:
                raise InvalidTimestampError(
                    f"End time {clip_data['end']}s exceeds video duration {video.duration_secs}s"
                )

    # Create batch job
    batch_job = await create_job(
        session,
        job_type="batch_clip_extract",
        video_id=video_id,
        status="pending",
    )

    clip_ids = []
    for clip_data in clips_data:
        clip = await create_clip(
            session,
            video_id=video_id,
            start_time=clip_data["start"],
            end_time=clip_data["end"],
            label=clip_data.get("label"),
            duration_secs=clip_data["end"] - clip_data["start"],
            status="pending",
        )
        clip_ids.append(clip.id)

    await session.flush()

    # Dispatch Celery task
    try:
        from worker.tasks.clip_tasks import batch_extract_clips
        task = batch_extract_clips.delay(
            str(batch_job.id),
            str(video_id),
            [{"clip_id": str(cid), **cd} for cid, cd in zip(clip_ids, clips_data)],
        )
        batch_job.celery_task_id = task.id
        await session.flush()
    except Exception as e:
        logger.warning("celery_dispatch_failed", error=str(e))

    return {"job_id": batch_job.id, "clip_ids": clip_ids}


async def trim_clip(session: AsyncSession, clip_id: uuid.UUID, new_start: float, new_end: float) -> dict:
    """Create a trimmed version of an existing clip."""
    from app.db.crud.clip import get_clip
    clip = await get_clip(session, clip_id)
    if not clip:
        from app.core.exceptions import ClipNotFoundError
        raise ClipNotFoundError(str(clip_id))

    # Create new clip record for the trimmed version
    trimmed_clip = await create_clip(
        session,
        video_id=clip.video_id,
        start_time=new_start,
        end_time=new_end,
        label=f"{clip.label or 'clip'}_trimmed",
        duration_secs=new_end - new_start,
        parent_clip_id=clip.id,
        status="pending",
    )

    job = await create_job(
        session,
        job_type="trim_clip",
        video_id=clip.video_id,
        clip_id=trimmed_clip.id,
        status="pending",
    )

    try:
        from worker.tasks.clip_tasks import trim_clip_task
        task = trim_clip_task.delay(str(job.id), str(clip.video_id), str(trimmed_clip.id), new_start, new_end)
        job.celery_task_id = task.id
        await session.flush()
    except Exception as e:
        logger.warning("celery_dispatch_failed", error=str(e))

    return {"job_id": job.id, "clip_id": trimmed_clip.id}


async def merge_clips(session: AsyncSession, clip_ids: list[uuid.UUID], label: str | None) -> dict:
    """Merge multiple clips into one."""
    from app.db.crud.clip import get_clip

    clips = []
    video_id = None
    for cid in clip_ids:
        clip = await get_clip(session, cid)
        if not clip:
            from app.core.exceptions import ClipNotFoundError
            raise ClipNotFoundError(str(cid))
        if clip.status != "ready":
            raise ValueError(f"Clip {cid} is not ready for merging (status: {clip.status})")
        clips.append(clip)
        if video_id is None:
            video_id = clip.video_id

    # Create merged clip record
    merged_clip = await create_clip(
        session,
        video_id=video_id,
        start_time=clips[0].start_time,
        end_time=clips[-1].end_time,
        label=label or "merged",
        status="pending",
    )

    job = await create_job(
        session,
        job_type="merge_clips",
        video_id=video_id,
        clip_id=merged_clip.id,
        status="pending",
    )

    try:
        from worker.tasks.clip_tasks import merge_clips_task
        task = merge_clips_task.delay(str(job.id), [str(cid) for cid in clip_ids], str(merged_clip.id))
        job.celery_task_id = task.id
        await session.flush()
    except Exception as e:
        logger.warning("celery_dispatch_failed", error=str(e))

    return {"job_id": job.id, "clip_id": merged_clip.id}
