import uuid
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.clip import Clip


async def create_clip(session: AsyncSession, **kwargs) -> Clip:
    clip = Clip(**kwargs)
    session.add(clip)
    await session.flush()
    return clip


async def get_clip(session: AsyncSession, clip_id: uuid.UUID) -> Clip | None:
    result = await session.execute(select(Clip).where(Clip.id == clip_id))
    return result.scalar_one_or_none()


async def list_clips(session: AsyncSession, video_id: uuid.UUID | None = None, offset: int = 0, limit: int = 50) -> list[Clip]:
    query = select(Clip).order_by(Clip.created_at.desc()).offset(offset).limit(limit)
    if video_id:
        query = query.where(Clip.video_id == video_id)
    result = await session.execute(query)
    return list(result.scalars().all())


async def update_clip(session: AsyncSession, clip_id: uuid.UUID, **kwargs) -> Clip | None:
    clip = await get_clip(session, clip_id)
    if clip:
        for key, value in kwargs.items():
            setattr(clip, key, value)
        await session.flush()
    return clip


async def delete_clip(session: AsyncSession, clip_id: uuid.UUID) -> bool:
    result = await session.execute(delete(Clip).where(Clip.id == clip_id))
    return result.rowcount > 0
