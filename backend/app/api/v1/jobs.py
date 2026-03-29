import uuid
from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.schemas.job import JobResponse, JobListResponse
from app.db.crud.job import get_job, list_jobs, update_job
from app.core.exceptions import JobNotFoundError

router = APIRouter()


@router.get("", response_model=JobListResponse)
async def list_all_jobs(
    status: str | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    """List all jobs with optional status filter."""
    jobs = await list_jobs(session, status=status, offset=offset, limit=limit)
    return JobListResponse(
        jobs=[JobResponse.model_validate(j) for j in jobs],
        total=len(jobs),
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: uuid.UUID = Path(...),
    session: AsyncSession = Depends(get_db),
):
    """Get job status and progress."""
    job = await get_job(session, job_id)
    if not job:
        raise JobNotFoundError(str(job_id))
    return JobResponse.model_validate(job)


@router.post("/{job_id}/cancel")
async def cancel_job(
    job_id: uuid.UUID = Path(...),
    session: AsyncSession = Depends(get_db),
):
    """Cancel a running job."""
    job = await get_job(session, job_id)
    if not job:
        raise JobNotFoundError(str(job_id))

    if job.status in ("pending", "running"):
        # Attempt to revoke Celery task
        if job.celery_task_id:
            try:
                from worker.app import celery_app
                celery_app.control.revoke(job.celery_task_id, terminate=True)
            except Exception:
                pass
        await update_job(session, job_id, status="cancelled")
        return {"status": "cancelled", "job_id": str(job_id)}

    return {"status": job.status, "message": "Job is not in a cancellable state"}


@router.post("/{job_id}/retry")
async def retry_job(
    job_id: uuid.UUID = Path(...),
    session: AsyncSession = Depends(get_db),
):
    """Retry a failed job."""
    job = await get_job(session, job_id)
    if not job:
        raise JobNotFoundError(str(job_id))

    if job.status != "failed":
        return {"message": "Only failed jobs can be retried"}

    # Reset job status
    await update_job(
        session, job_id,
        status="pending",
        progress_pct=0,
        error_message=None,
        retry_count=job.retry_count + 1,
    )

    # Re-dispatch based on job type
    # This is simplified - in production you'd store task args
    return {"status": "pending", "job_id": str(job_id), "retry_count": job.retry_count + 1}
