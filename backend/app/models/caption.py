import uuid
from sqlalchemy import String, Float, Integer, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDMixin, TimestampMixin


class Caption(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "captions"

    video_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    model_size: Mapped[str] = mapped_column(String(20), nullable=False)
    language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    full_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)

    # Relationships
    video = relationship("Video", back_populates="captions")
    segments = relationship("CaptionSegment", back_populates="caption", cascade="all, delete-orphan", order_by="CaptionSegment.segment_index")
    style = relationship("CaptionStyle", back_populates="caption", uselist=False, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Caption {self.id} video={self.video_id} ({self.status})>"


class CaptionSegment(Base, UUIDMixin):
    __tablename__ = "caption_segments"

    caption_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("captions.id", ondelete="CASCADE"), nullable=False)
    segment_index: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[float] = mapped_column(Float, nullable=False)
    end_time: Mapped[float] = mapped_column(Float, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    words_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    caption = relationship("Caption", back_populates="segments")

    def __repr__(self) -> str:
        return f"<CaptionSegment {self.segment_index} [{self.start_time}-{self.end_time}]>"


class CaptionStyle(Base, UUIDMixin):
    __tablename__ = "caption_styles"

    caption_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("captions.id", ondelete="CASCADE"), nullable=False, unique=True)
    font_family: Mapped[str] = mapped_column(String(100), default="Arial", nullable=False)
    font_size: Mapped[int] = mapped_column(Integer, default=48, nullable=False)
    primary_color: Mapped[str] = mapped_column(String(20), default="#FFFFFF", nullable=False)
    outline_color: Mapped[str] = mapped_column(String(20), default="#000000", nullable=False)
    highlight_color: Mapped[str] = mapped_column(String(20), default="#FFFF00", nullable=False)
    highlight_words: Mapped[list | None] = mapped_column(ARRAY(String), nullable=True)
    position: Mapped[str] = mapped_column(String(20), default="bottom", nullable=False)
    bold: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    animation_type: Mapped[str] = mapped_column(String(30), default="none", nullable=False)

    # Relationships
    caption = relationship("Caption", back_populates="style")

    def __repr__(self) -> str:
        return f"<CaptionStyle {self.id} font={self.font_family} anim={self.animation_type}>"
