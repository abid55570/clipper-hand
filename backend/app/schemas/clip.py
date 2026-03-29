from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from uuid import UUID


class ClipTimestamp(BaseModel):
    start: float = Field(..., ge=0, description="Start time in seconds")
    end: float = Field(..., gt=0, description="End time in seconds")
    label: str | None = Field(None, max_length=200)

    @model_validator(mode="after")
    def validate_timestamps(self):
        if self.end <= self.start:
            raise ValueError("End time must be greater than start time")
        return self


class CreateClipsRequest(BaseModel):
    clips: list[ClipTimestamp] = Field(..., min_length=1, max_length=100)


class CreateClipsResponse(BaseModel):
    job_id: UUID
    clip_ids: list[UUID]


class TrimClipRequest(BaseModel):
    new_start: float = Field(..., ge=0)
    new_end: float = Field(..., gt=0)

    @model_validator(mode="after")
    def validate_timestamps(self):
        if self.new_end <= self.new_start:
            raise ValueError("End time must be greater than start time")
        return self


class MergeClipsRequest(BaseModel):
    clip_ids: list[UUID] = Field(..., min_length=2, max_length=50)
    label: str | None = Field(None, max_length=200)


class BatchProcessRequest(BaseModel):
    video_id: UUID
    clips: list[ClipTimestamp] = Field(..., min_length=1, max_length=100)


class ClipResponse(BaseModel):
    id: UUID
    video_id: UUID
    label: str | None
    start_time: float
    end_time: float
    duration_secs: float | None
    file_size_bytes: int | None
    status: str
    parent_clip_id: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ClipListResponse(BaseModel):
    clips: list[ClipResponse]
    total: int
