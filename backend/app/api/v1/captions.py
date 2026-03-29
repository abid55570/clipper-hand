import uuid
from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.schemas.caption import (
    TranscribeRequest, TranscribeResponse,
    CaptionResponse, CaptionSegmentResponse, WordTimestamp,
    CaptionStyleRequest, CaptionStyleResponse,
    BurnSubtitlesRequest,
)
from app.services import caption_service
from app.db.crud.caption import get_caption, get_captions_for_video, get_caption_segments
from app.core.exceptions import CaptionNotFoundError

router = APIRouter()


@router.post("/videos/{video_id}/transcribe", response_model=TranscribeResponse)
async def transcribe_video(
    video_id: uuid.UUID = Path(...),
    request: TranscribeRequest = TranscribeRequest(),
    session: AsyncSession = Depends(get_db),
):
    """Start speech-to-text transcription."""
    result = await caption_service.start_transcription(session, video_id, request.model_size)
    return TranscribeResponse(**result)


@router.get("/videos/{video_id}/captions")
async def get_video_captions(
    video_id: uuid.UUID = Path(...),
    session: AsyncSession = Depends(get_db),
):
    """Get all captions for a video."""
    captions = await get_captions_for_video(session, video_id)
    result = []
    for cap in captions:
        segments = await get_caption_segments(session, cap.id)
        seg_responses = []
        for seg in segments:
            words = None
            if seg.words_json:
                words = [WordTimestamp(**w) for w in seg.words_json]
            seg_responses.append(CaptionSegmentResponse(
                id=seg.id,
                segment_index=seg.segment_index,
                start_time=seg.start_time,
                end_time=seg.end_time,
                text=seg.text,
                words=words,
            ))
        result.append({
            "id": cap.id,
            "video_id": cap.video_id,
            "model_size": cap.model_size,
            "language": cap.language,
            "full_text": cap.full_text,
            "status": cap.status,
            "segments": seg_responses,
            "created_at": cap.created_at,
        })
    return {"captions": result}


@router.put("/{caption_id}/style", response_model=CaptionStyleResponse)
async def update_caption_style(
    caption_id: uuid.UUID = Path(...),
    request: CaptionStyleRequest = ...,
    session: AsyncSession = Depends(get_db),
):
    """Update caption styling."""
    caption = await get_caption(session, caption_id)
    if not caption:
        raise CaptionNotFoundError(str(caption_id))
    await caption_service.update_caption_style(session, caption_id, request.model_dump())
    from app.db.crud.caption import create_or_update_caption_style
    style = await create_or_update_caption_style(session, caption_id, **request.model_dump())
    return CaptionStyleResponse.model_validate(style)


@router.post("/clips/{clip_id}/burn-subtitles")
async def burn_subtitles(
    clip_id: uuid.UUID = Path(...),
    request: BurnSubtitlesRequest = ...,
    session: AsyncSession = Depends(get_db),
):
    """Burn subtitles into a clip."""
    style_data = request.style.model_dump() if request.style else None
    result = await caption_service.start_burn_subtitles(session, clip_id, request.caption_id, style_data)
    return result
