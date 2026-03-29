import uuid
from sqlalchemy import String, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDMixin, TimestampMixin


class Job(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "jobs"

    celery_task_id: Mapped[str | None] = mapped_column(String(200), unique=True, nullable=True)
    job_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False, index=True)
    progress_pct: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    result_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    video_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=True)
    clip_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("clips.id"), nullable=True)

    # Relationships
    video = relationship("Video", back_populates="jobs")
    clip = relationship("Clip", back_populates="jobs")

    def __repr__(self) -> str:
        return f"<Job {self.id} type={self.job_type} status={self.status} progress={self.progress_pct}%>"
