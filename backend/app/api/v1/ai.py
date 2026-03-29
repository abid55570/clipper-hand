import uuid
from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.schemas.ai import (
    DetectHighlightsResponse, HighlightListResponse, HighlightResponse,
    GenerateContentResponse, GenerateHookResponse, DetectSpeakersResponse,
)
from app.services import ai_service
from app.db.crud.export import get_highlights_for_video
from app.db.crud.job import get_job

router = APIRouter()


@router.post("/videos/{video_id}/detect-highlights", response_model=DetectHighlightsResponse)
async def detect_highlights(
    video_id: uuid.UUID = Path(...),
    session: AsyncSession = Depends(get_db),
):
    """Start AI highlight detection."""
    result = await ai_service.start_highlight_detection(session, video_id)
    return DetectHighlightsResponse(**result)


@router.get("/videos/{video_id}/highlights", response_model=HighlightListResponse)
async def get_highlights(
    video_id: uuid.UUID = Path(...),
    session: AsyncSession = Depends(get_db),
):
    """Get detected highlights for a video."""
    highlights = await get_highlights_for_video(session, video_id)
    return HighlightListResponse(
        highlights=[HighlightResponse.model_validate(h) for h in highlights],
        video_id=video_id,
    )


@router.post("/clips/{clip_id}/generate-content", response_model=GenerateContentResponse)
async def generate_content(
    clip_id: uuid.UUID = Path(...),
    session: AsyncSession = Depends(get_db),
):
    """Generate title, description, and hashtags for a clip."""
    result = await ai_service.start_content_generation(session, clip_id)
    return GenerateContentResponse(**result)


@router.get("/clips/{clip_id}/content")
async def get_generated_content(
    clip_id: uuid.UUID = Path(...),
    session: AsyncSession = Depends(get_db),
):
    """Get generated content for a clip (from job result)."""
    from app.db.crud.job import list_jobs
    from sqlalchemy import select
    from app.models.job import Job
    result = await session.execute(
        select(Job).where(Job.clip_id == clip_id, Job.job_type == "generate_content", Job.status == "completed").order_by(Job.created_at.desc()).limit(1)
    )
    job = result.scalar_one_or_none()
    if job and job.result_json:
        return job.result_json
    return {"title": "", "description": "", "hashtags": []}


@router.post("/clips/{clip_id}/generate-hook", response_model=GenerateHookResponse)
async def generate_hook(
    clip_id: uuid.UUID = Path(...),
    session: AsyncSession = Depends(get_db),
):
    """Generate engaging hook text for a clip."""
    result = await ai_service.start_hook_generation(session, clip_id)
    # Return immediate placeholder; real result via job polling
    return GenerateHookResponse(hooks=[])


@router.post("/videos/{video_id}/detect-speakers", response_model=DetectSpeakersResponse)
async def detect_speakers(
    video_id: uuid.UUID = Path(...),
    session: AsyncSession = Depends(get_db),
):
    """Start speaker detection (placeholder)."""
    result = await ai_service.start_speaker_detection(session, video_id)
    return DetectSpeakersResponse(**result)
