from sqlalchemy import String, Float, Integer, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDMixin, TimestampMixin


class Video(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "videos"

    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    original_name: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    duration_secs: Mapped[float | None] = mapped_column(Float, nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fps: Mapped[float | None] = mapped_column(Float, nullable=True)
    codec: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="uploading", nullable=False)

    # Relationships
    clips = relationship("Clip", back_populates="video", cascade="all, delete-orphan")
    captions = relationship("Caption", back_populates="video", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="video", cascade="all, delete-orphan")
    highlights = relationship("Highlight", back_populates="video", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Video {self.id} '{self.original_name}' ({self.status})>"
