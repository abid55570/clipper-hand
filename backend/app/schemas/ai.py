from pydantic import BaseModel
from uuid import UUID


class DetectHighlightsResponse(BaseModel):
    job_id: UUID


class HighlightResponse(BaseModel):
    id: UUID
    start_time: float
    end_time: float
    score: float | None
    reason: str | None
    source: str | None

    model_config = {"from_attributes": True}


class HighlightListResponse(BaseModel):
    highlights: list[HighlightResponse]
    video_id: UUID


class GenerateContentResponse(BaseModel):
    job_id: UUID


class ContentResult(BaseModel):
    title: str
    description: str
    hashtags: list[str]


class HookItem(BaseModel):
    text: str
    style: str = "bold"


class GenerateHookResponse(BaseModel):
    hooks: list[HookItem]


class DetectSpeakersResponse(BaseModel):
    job_id: UUID


class SpeakerSegment(BaseModel):
    speaker_id: str
    start_time: float
    end_time: float
    confidence: float | None = None
