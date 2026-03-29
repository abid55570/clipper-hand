import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from app.models.job import Job


async def create_job(session: AsyncSession, **kwargs) -> Job:
    job = Job(**kwargs)
    session.add(job)
    await session.flush()
    return job


async def get_job(session: AsyncSession, job_id: uuid.UUID) -> Job | None:
    result = await session.execute(select(Job).where(Job.id == job_id))
    return result.scalar_one_or_none()


async def list_jobs(session: AsyncSession, status: str | None = None, offset: int = 0, limit: int = 50) -> list[Job]:
    query = select(Job).order_by(Job.created_at.desc()).offset(offset).limit(limit)
    if status:
        query = query.where(Job.status == status)
    result = await session.execute(query)
    return list(result.scalars().all())


async def update_job(session: AsyncSession, job_id: uuid.UUID, **kwargs) -> Job | None:
    job = await get_job(session, job_id)
    if job:
        for key, value in kwargs.items():
            setattr(job, key, value)
        await session.flush()
    return job


# Sync versions for Celery workers
def create_job_sync(session: Session, **kwargs) -> Job:
    job = Job(**kwargs)
    session.add(job)
    session.flush()
    return job


def get_job_sync(session: Session, job_id: uuid.UUID) -> Job | None:
    return session.query(Job).filter(Job.id == job_id).first()


def update_job_sync(session: Session, job_id: uuid.UUID, **kwargs) -> Job | None:
    job = get_job_sync(session, job_id)
    if job:
        for key, value in kwargs.items():
            setattr(job, key, value)
        session.flush()
    return job
