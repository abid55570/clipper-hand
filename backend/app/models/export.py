import uuid
from sqlalchemy import String, Integer, Float, BigInteger, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDMixin, TimestampMixin


class Export(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "exports"

    clip_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clips.id", ondelete="CASCADE"), nullable=False)
    job_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=True)
    aspect_ratio: Mapped[str] = mapped_column(String(10), nullable=False)
    platform: Mapped[str | None] = mapped_column(String(30), nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    effects_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)

    # Relationships
    clip = relationship("Clip", back_populates="exports")

    def __repr__(self) -> str:
        return f"<Export {self.id} ratio={self.aspect_ratio} ({self.status})>"


class Highlight(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "highlights"

    video_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    start_time: Mapped[float] = mapped_column(Float, nullable=False)
    end_time: Mapped[float] = mapped_column(Float, nullable=False)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str | None] = mapped_column(String(30), nullable=True)

    # Relationships
    video = relationship("Video", back_populates="highlights")

    def __repr__(self) -> str:
        return f"<Highlight {self.id} [{self.start_time}-{self.end_time}] score={self.score}>"
