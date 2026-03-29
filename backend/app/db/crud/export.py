import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.export import Export, Highlight


async def create_export(session: AsyncSession, **kwargs) -> Export:
    export = Export(**kwargs)
    session.add(export)
    await session.flush()
    return export


async def get_export(session: AsyncSession, export_id: uuid.UUID) -> Export | None:
    result = await session.execute(select(Export).where(Export.id == export_id))
    return result.scalar_one_or_none()


async def update_export(session: AsyncSession, export_id: uuid.UUID, **kwargs) -> Export | None:
    export = await get_export(session, export_id)
    if export:
        for key, value in kwargs.items():
            setattr(export, key, value)
        await session.flush()
    return export


async def create_highlight(session: AsyncSession, **kwargs) -> Highlight:
    highlight = Highlight(**kwargs)
    session.add(highlight)
    await session.flush()
    return highlight


async def get_highlights_for_video(session: AsyncSession, video_id: uuid.UUID) -> list[Highlight]:
    result = await session.execute(
        select(Highlight)
        .where(Highlight.video_id == video_id)
        .order_by(Highlight.score.desc().nullslast())
    )
    return list(result.scalars().all())


async def create_highlights_bulk(session: AsyncSession, video_id: uuid.UUID, highlights: list[dict]) -> list[Highlight]:
    models = []
    for h in highlights:
        highlight = Highlight(video_id=video_id, **h)
        session.add(highlight)
        models.append(highlight)
    await session.flush()
    return models
