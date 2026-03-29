import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.exceptions import AppError
from app.api.middleware.error_handler import app_error_handler
from app.api.middleware.logging_mw import LoggingMiddleware
from app.api.middleware.rate_limit import RateLimitMiddleware
from app.api.router import api_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    setup_logging()
    # Create upload and media directories
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.media_dir, exist_ok=True)
    logger.info("app_started", upload_dir=settings.upload_dir, media_dir=settings.media_dir)
    yield
    logger.info("app_shutdown")


app = FastAPI(
    title="AI Video Clipping Platform",
    description="Upload, clip, caption, and export videos with AI-powered features.",
    version="1.0.0",
    lifespan=lifespan,
)

# Middleware (order matters: last added = first executed)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(AppError, app_error_handler)

# Routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
