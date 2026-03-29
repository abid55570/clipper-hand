from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import AppError
from app.core.logging import get_logger

logger = get_logger(__name__)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Handle application-specific errors."""
    logger.warning("app_error", error=exc.message, status_code=exc.status_code, path=request.url.path)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "status_code": exc.status_code},
    )
