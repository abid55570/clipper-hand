from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class UploadInitRequest(BaseModel):
    filename: str = Field(..., min_length=1, max_length=500)
    file_size: int = Field(..., gt=0, description="Total file size in bytes")
    content_type: str = Field(default="video/mp4")


class UploadInitResponse(BaseModel):
    upload_id: str
    chunk_size: int
    total_chunks: int


class UploadChunkResponse(BaseModel):
    chunk_index: int
    received: bool


class UploadCompleteResponse(BaseModel):
    video_id: UUID
    job_id: UUID
    message: str = "Upload complete. Processing metadata."


class VideoResponse(BaseModel):
    id: UUID
    filename: str
    original_name: str
    file_size_bytes: int
    duration_secs: float | None
    width: int | None
    height: int | None
    fps: float | None
    codec: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class VideoListResponse(BaseModel):
    videos: list[VideoResponse]
    total: int
