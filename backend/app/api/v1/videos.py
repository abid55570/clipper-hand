import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Path, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.schemas.video import (
    UploadInitRequest, UploadInitResponse,
    UploadChunkResponse, UploadCompleteResponse,
    VideoResponse, VideoListResponse,
)
from app.services import video_service
from app.db.crud.video import get_video, list_videos, delete_video
from app.core.exceptions import VideoNotFoundError

router = APIRouter()


@router.post("/upload/init", response_model=UploadInitResponse)
async def init_upload(request: UploadInitRequest, session: AsyncSession = Depends(get_db)):
    """Initialize a chunked upload session."""
    result = await video_service.init_upload(
        session, request.filename, request.file_size, request.content_type
    )
    return UploadInitResponse(**result)


@router.post("/upload/chunk/{upload_id}", response_model=UploadChunkResponse)
async def upload_chunk(
    upload_id: str = Path(...),
    chunk_index: int = Query(..., ge=0),
    file: UploadFile = File(...),
):
    """Upload a single chunk."""
    data = await file.read()
    result = await video_service.save_upload_chunk(upload_id, chunk_index, data)
    return UploadChunkResponse(**result)


@router.post("/upload/complete/{upload_id}", response_model=UploadCompleteResponse)
async def complete_upload(
    upload_id: str = Path(...),
    session: AsyncSession = Depends(get_db),
):
    """Finalize the upload and begin processing."""
    result = await video_service.complete_upload(session, upload_id)
    return UploadCompleteResponse(**result)


@router.get("", response_model=VideoListResponse)
async def list_all_videos(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    """List all uploaded videos."""
    videos = await list_videos(session, offset=offset, limit=limit)
    return VideoListResponse(
        videos=[VideoResponse.model_validate(v) for v in videos],
        total=len(videos),
    )


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video_detail(
    video_id: uuid.UUID = Path(...),
    session: AsyncSession = Depends(get_db),
):
    """Get video details."""
    video = await get_video(session, video_id)
    if not video:
        raise VideoNotFoundError(str(video_id))
    return VideoResponse.model_validate(video)


@router.delete("/{video_id}", status_code=204)
async def delete_video_endpoint(
    video_id: uuid.UUID = Path(...),
    session: AsyncSession = Depends(get_db),
):
    """Delete a video and all associated data."""
    video = await get_video(session, video_id)
    if not video:
        raise VideoNotFoundError(str(video_id))
    from app.services.storage_service import storage
    storage.delete(video.file_path)
    await delete_video(session, video_id)
