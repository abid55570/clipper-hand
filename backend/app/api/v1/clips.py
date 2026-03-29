import uuid
from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.schemas.clip import (
    CreateClipsRequest, CreateClipsResponse,
    TrimClipRequest, MergeClipsRequest, BatchProcessRequest,
    ClipResponse, ClipListResponse,
)
from app.schemas.job import JobResponse
from app.services import clip_service
from app.db.crud.clip import get_clip, list_clips, delete_clip
from app.core.exceptions import ClipNotFoundError

router = APIRouter()


@router.post("/video/{video_id}", response_model=CreateClipsResponse)
async def create_clips(
    video_id: uuid.UUID = Path(...),
    request: CreateClipsRequest = ...,
    session: AsyncSession = Depends(get_db),
):
    """Create clips from timestamps."""
    clips_data = [c.model_dump() for c in request.clips]
    result = await clip_service.create_clips_from_timestamps(session, video_id, clips_data)
    return CreateClipsResponse(**result)


@router.get("", response_model=ClipListResponse)
async def list_all_clips(
    video_id: uuid.UUID | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    """List clips, optionally filtered by video."""
    clips = await list_clips(session, video_id=video_id, offset=offset, limit=limit)
    return ClipListResponse(
        clips=[ClipResponse.model_validate(c) for c in clips],
        total=len(clips),
    )


@router.get("/{clip_id}", response_model=ClipResponse)
async def get_clip_detail(
    clip_id: uuid.UUID = Path(...),
    session: AsyncSession = Depends(get_db),
):
    """Get clip details."""
    clip = await get_clip(session, clip_id)
    if not clip:
        raise ClipNotFoundError(str(clip_id))
    return ClipResponse.model_validate(clip)


@router.get("/{clip_id}/download")
async def download_clip(
    clip_id: uuid.UUID = Path(...),
    session: AsyncSession = Depends(get_db),
):
    """Download a processed clip."""
    clip = await get_clip(session, clip_id)
    if not clip:
        raise ClipNotFoundError(str(clip_id))
    if not clip.file_path or clip.status != "ready":
        raise ClipNotFoundError(f"Clip {clip_id} is not ready for download")
    return FileResponse(
        clip.file_path,
        media_type="video/mp4",
        filename=f"{clip.label or 'clip'}_{clip.id}.mp4",
    )


@router.post("/{clip_id}/trim")
async def trim_clip_endpoint(
    clip_id: uuid.UUID = Path(...),
    request: TrimClipRequest = ...,
    session: AsyncSession = Depends(get_db),
):
    """Trim an existing clip."""
    result = await clip_service.trim_clip(session, clip_id, request.new_start, request.new_end)
    return result


@router.post("/merge")
async def merge_clips_endpoint(
    request: MergeClipsRequest,
    session: AsyncSession = Depends(get_db),
):
    """Merge multiple clips into one."""
    result = await clip_service.merge_clips(session, request.clip_ids, request.label)
    return result


@router.post("/batch")
async def batch_process(
    request: BatchProcessRequest,
    session: AsyncSession = Depends(get_db),
):
    """Batch process multiple clips from a video."""
    clips_data = [c.model_dump() for c in request.clips]
    result = await clip_service.create_clips_from_timestamps(session, request.video_id, clips_data)
    return result


@router.delete("/{clip_id}", status_code=204)
async def delete_clip_endpoint(
    clip_id: uuid.UUID = Path(...),
    session: AsyncSession = Depends(get_db),
):
    """Delete a clip."""
    clip = await get_clip(session, clip_id)
    if not clip:
        raise ClipNotFoundError(str(clip_id))
    if clip.file_path:
        from app.services.storage_service import storage
        storage.delete(clip.file_path)
    await delete_clip(session, clip_id)
