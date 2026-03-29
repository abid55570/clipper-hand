from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class TranscribeRequest(BaseModel):
    model_size: str = Field(default="base", pattern="^(tiny|base|small|medium|large)$")


class TranscribeResponse(BaseModel):
    job_id: UUID
    caption_id: UUID


class WordTimestamp(BaseModel):
    word: str
    start: float
    end: float
    probability: float | None = None


class CaptionSegmentResponse(BaseModel):
    id: UUID
    segment_index: int
    start_time: float
    end_time: float
    text: str
    words: list[WordTimestamp] | None = None

    model_config = {"from_attributes": True}


class CaptionResponse(BaseModel):
    id: UUID
    video_id: UUID
    model_size: str
    language: str | None
    full_text: str | None
    status: str
    segments: list[CaptionSegmentResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class CaptionStyleRequest(BaseModel):
    font_family: str = Field(default="Arial", max_length=100)
    font_size: int = Field(default=48, ge=8, le=200)
    primary_color: str = Field(default="#FFFFFF", pattern="^#[0-9A-Fa-f]{6}$")
    outline_color: str = Field(default="#000000", pattern="^#[0-9A-Fa-f]{6}$")
    highlight_color: str = Field(default="#FFFF00", pattern="^#[0-9A-Fa-f]{6}$")
    highlight_words: list[str] | None = None
    position: str = Field(default="bottom", pattern="^(top|center|bottom)$")
    bold: bool = False
    animation_type: str = Field(default="none", pattern="^(none|word_by_word|karaoke|fade|pop|slide)$")


class CaptionStyleResponse(BaseModel):
    id: UUID
    caption_id: UUID
    font_family: str
    font_size: int
    primary_color: str
    outline_color: str
    highlight_color: str
    highlight_words: list[str] | None
    position: str
    bold: bool
    animation_type: str

    model_config = {"from_attributes": True}


class BurnSubtitlesRequest(BaseModel):
    caption_id: UUID
    style: CaptionStyleRequest | None = None
