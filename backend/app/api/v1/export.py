import uuid
from fastapi import APIRouter, Depends, Path
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.schemas.export import ExportRequest, ExportResponse, ExportCreateResponse
from app.services import export_service
from app.db.crud.export import get_export
from app.core.exceptions import ExportNotFoundError

router = APIRouter()


@router.post("/clips/{clip_id}/export", response_model=ExportCreateResponse)
async def create_export(
    clip_id: uuid.UUID = Path(...),
    request: ExportRequest = ...,
    session: AsyncSession = Depends(get_db),
):
    """Export a clip with specified aspect ratio and effects."""
    effects = request.effects.model_dump() if request.effects else None
    result = await export_service.start_export(
        session, clip_id, request.aspect_ratio, request.platform, effects
    )
    return ExportCreateResponse(**result)


@router.get("/{export_id}", response_model=ExportResponse)
async def get_export_detail(
    export_id: uuid.UUID = Path(...),
    session: AsyncSession = Depends(get_db),
):
    """Get export details."""
    export = await get_export(session, export_id)
    if not export:
        raise ExportNotFoundError(str(export_id))
    return ExportResponse.model_validate(export)


@router.get("/{export_id}/download")
async def download_export(
    export_id: uuid.UUID = Path(...),
    session: AsyncSession = Depends(get_db),
):
    """Download an exported video."""
    export = await get_export(session, export_id)
    if not export:
        raise ExportNotFoundError(str(export_id))
    if not export.file_path or export.status != "ready":
        raise ExportNotFoundError(f"Export {export_id} is not ready for download")
    return FileResponse(
        export.file_path,
        media_type="video/mp4",
        filename=f"export_{export.aspect_ratio.replace(':', 'x')}_{export.id}.mp4",
    )
