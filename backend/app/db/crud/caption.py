import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.caption import Caption, CaptionSegment, CaptionStyle


async def create_caption(session: AsyncSession, **kwargs) -> Caption:
    caption = Caption(**kwargs)
    session.add(caption)
    await session.flush()
    return caption


async def get_caption(session: AsyncSession, caption_id: uuid.UUID) -> Caption | None:
    result = await session.execute(select(Caption).where(Caption.id == caption_id))
    return result.scalar_one_or_none()


async def get_captions_for_video(session: AsyncSession, video_id: uuid.UUID) -> list[Caption]:
    result = await session.execute(
        select(Caption).where(Caption.video_id == video_id).order_by(Caption.created_at.desc())
    )
    return list(result.scalars().all())


async def update_caption(session: AsyncSession, caption_id: uuid.UUID, **kwargs) -> Caption | None:
    caption = await get_caption(session, caption_id)
    if caption:
        for key, value in kwargs.items():
            setattr(caption, key, value)
        await session.flush()
    return caption


async def create_caption_segments(session: AsyncSession, caption_id: uuid.UUID, segments: list[dict]) -> list[CaptionSegment]:
    segment_models = []
    for i, seg in enumerate(segments):
        segment = CaptionSegment(
            caption_id=caption_id,
            segment_index=i,
            start_time=seg["start"],
            end_time=seg["end"],
            text=seg["text"],
            words_json=seg.get("words"),
        )
        session.add(segment)
        segment_models.append(segment)
    await session.flush()
    return segment_models


async def get_caption_segments(session: AsyncSession, caption_id: uuid.UUID) -> list[CaptionSegment]:
    result = await session.execute(
        select(CaptionSegment)
        .where(CaptionSegment.caption_id == caption_id)
        .order_by(CaptionSegment.segment_index)
    )
    return list(result.scalars().all())


async def create_or_update_caption_style(session: AsyncSession, caption_id: uuid.UUID, **kwargs) -> CaptionStyle:
    result = await session.execute(
        select(CaptionStyle).where(CaptionStyle.caption_id == caption_id)
    )
    style = result.scalar_one_or_none()
    if style:
        for key, value in kwargs.items():
            setattr(style, key, value)
    else:
        style = CaptionStyle(caption_id=caption_id, **kwargs)
        session.add(style)
    await session.flush()
    return style
