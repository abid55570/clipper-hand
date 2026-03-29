from fastapi import APIRouter
from app.api.v1 import videos, clips, captions, ai, jobs, export

api_router = APIRouter()

api_router.include_router(videos.router, prefix="/videos", tags=["Videos"])
api_router.include_router(clips.router, prefix="/clips", tags=["Clips"])
api_router.include_router(captions.router, prefix="/captions", tags=["Captions"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(export.router, prefix="/exports", tags=["Exports"])
