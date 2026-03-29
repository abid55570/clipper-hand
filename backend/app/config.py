from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://clipper:clipper_pass@localhost:5432/clipper_db"
    database_url_sync: str = "postgresql://clipper:clipper_pass@localhost:5432/clipper_db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # Storage
    upload_dir: str = "/app/uploads"
    media_dir: str = "/app/media"
    max_upload_size_gb: float = 10.0
    chunk_size_mb: int = 5

    # Video Processing
    ffmpeg_threads: int = 2
    whisper_model_size: str = "base"

    # AI
    openai_api_key: str = ""

    # App
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def max_upload_size_bytes(self) -> int:
        return int(self.max_upload_size_gb * 1024 * 1024 * 1024)

    @property
    def chunk_size_bytes(self) -> int:
        return self.chunk_size_mb * 1024 * 1024

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
