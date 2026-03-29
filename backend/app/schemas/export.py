from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class EffectsConfig(BaseModel):
    zoom: bool = False
    jump_cut: bool = False
    jump_cut_threshold_db: float = Field(default=-40.0, description="Silence threshold in dB")
    jump_cut_min_silence: float = Field(default=0.5, description="Min silence duration in seconds")
    text_animation: str | None = Field(None, pattern="^(none|fade|pop|slide|typewriter)$")
    text_content: str | None = None


class ExportRequest(BaseModel):
    aspect_ratio: str = Field(..., pattern="^(16:9|9:16|1:1|4:5)$")
    platform: str | None = Field(None, pattern="^(tiktok|instagram|youtube_shorts|twitter)$")
    effects: EffectsConfig | None = None


class ExportResponse(BaseModel):
    id: UUID
    clip_id: UUID
    job_id: UUID | None
    aspect_ratio: str
    platform: str | None
    width: int | None
    height: int | None
    file_size_bytes: int | None
    effects_json: dict | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ExportCreateResponse(BaseModel):
    job_id: UUID
    export_id: UUID
