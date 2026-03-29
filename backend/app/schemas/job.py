from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class JobResponse(BaseModel):
    id: UUID
    celery_task_id: str | None
    job_type: str
    status: str
    progress_pct: int
    result_json: dict | None
    error_message: str | None
    retry_count: int
    video_id: UUID | None
    clip_id: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    jobs: list[JobResponse]
    total: int
