import uuid
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.video import Video


async def create_video(session: AsyncSession, **kwargs) -> Video:
    video = Video(**kwargs)
    session.add(video)
    await session.flush()
    return video


async def get_video(session: AsyncSession, video_id: uuid.UUID) -> Video | None:
    result = await session.execute(select(Video).where(Video.id == video_id))
    return result.scalar_one_or_none()


async def list_videos(session: AsyncSession, offset: int = 0, limit: int = 50) -> list[Video]:
    result = await session.execute(
        select(Video).order_by(Video.created_at.desc()).offset(offset).limit(limit)
    )
    return list(result.scalars().all())


async def update_video(session: AsyncSession, video_id: uuid.UUID, **kwargs) -> Video | None:
    video = await get_video(session, video_id)
    if video:
        for key, value in kwargs.items():
            setattr(video, key, value)
        await session.flush()
    return video


async def delete_video(session: AsyncSession, video_id: uuid.UUID) -> bool:
    result = await session.execute(delete(Video).where(Video.id == video_id))
    return result.rowcount > 0
