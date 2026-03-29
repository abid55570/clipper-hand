import uuid
from sqlalchemy import String, Float, Integer, BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDMixin, TimestampMixin


class Clip(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "clips"

    video_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    start_time: Mapped[float] = mapped_column(Float, nullable=False)
    end_time: Mapped[float] = mapped_column(Float, nullable=False)
    duration_secs: Mapped[float | None] = mapped_column(Float, nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    parent_clip_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("clips.id"), nullable=True)

    # Relationships
    video = relationship("Video", back_populates="clips")
    exports = relationship("Export", back_populates="clip", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="clip")
    parent_clip = relationship("Clip", remote_side="Clip.id")

    @property
    def computed_duration(self) -> float:
        return self.end_time - self.start_time

    def __repr__(self) -> str:
        return f"<Clip {self.id} [{self.start_time}-{self.end_time}] ({self.status})>"
