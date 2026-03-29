#!/usr/bin/env python3
"""Seed the database with sample data for development."""
import os
import sys
import uuid
from datetime import datetime, timezone

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Video, Clip, Job


def seed():
    engine = create_engine(
        os.environ.get("DATABASE_URL_SYNC", "postgresql://clipper:clipper_pass@localhost:5432/clipper_db")
    )
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create sample video
    video = Video(
        id=uuid.uuid4(),
        filename="sample_video.mp4",
        original_name="My Sample Video.mp4",
        file_path="/app/uploads/sample_video.mp4",
        file_size_bytes=104857600,  # 100 MB
        duration_secs=3600.0,  # 1 hour
        width=1920,
        height=1080,
        fps=30.0,
        codec="h264",
        status="ready",
    )
    session.add(video)

    # Create sample clips
    clips_data = [
        {"start": 120.0, "end": 180.0, "label": "Introduction"},
        {"start": 600.0, "end": 660.0, "label": "Key Point 1"},
        {"start": 1800.0, "end": 1860.0, "label": "Highlight Moment"},
    ]
    for cd in clips_data:
        clip = Clip(
            video_id=video.id,
            start_time=cd["start"],
            end_time=cd["end"],
            label=cd["label"],
            duration_secs=cd["end"] - cd["start"],
            status="pending",
        )
        session.add(clip)

    session.commit()
    print(f"Seeded: 1 video, {len(clips_data)} clips")
    session.close()


if __name__ == "__main__":
    seed()
