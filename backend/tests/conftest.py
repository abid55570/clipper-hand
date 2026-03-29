"""Test fixtures and configuration."""
import os
import uuid
import asyncio
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_video_path(tmp_path):
    """Create a small test video using ffmpeg."""
    output = tmp_path / "test_video.mp4"
    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", "testsrc=duration=10:size=640x480:rate=30",
                "-f", "lavfi", "-i", "sine=frequency=440:duration=10",
                "-c:v", "libx264", "-c:a", "aac",
                "-shortest",
                str(output),
            ],
            capture_output=True, timeout=30, check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        # If ffmpeg not available, create a dummy file
        output.write_bytes(b"\x00\x00\x00\x1cftypisom" + b"\x00" * 1000)
    return str(output)


@pytest.fixture
def mock_db_session():
    """Create a mock async DB session."""
    session = AsyncMock(spec=AsyncSession)
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session


@pytest.fixture
def test_client():
    """Create a FastAPI test client with mocked dependencies."""
    from app.main import app
    from app.dependencies import get_db

    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.flush = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()

    async def override_get_db():
        yield mock_session

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client, mock_session
    app.dependency_overrides.clear()


@pytest.fixture
def sample_video_metadata():
    """Sample video metadata for testing."""
    return {
        "duration_secs": 120.5,
        "width": 1920,
        "height": 1080,
        "fps": 30.0,
        "codec": "h264",
    }


@pytest.fixture
def sample_clip_data():
    """Sample clip creation data."""
    return [
        {"start": 10.0, "end": 30.0, "label": "highlight_1"},
        {"start": 45.5, "end": 60.0, "label": "highlight_2"},
        {"start": 90.0, "end": 110.0, "label": "conclusion"},
    ]


@pytest.fixture
def sample_transcript_segments():
    """Sample Whisper transcription output."""
    return [
        {
            "start": 0.0,
            "end": 5.0,
            "text": "Hello and welcome to this video",
            "words": [
                {"word": "Hello", "start": 0.0, "end": 0.5, "probability": 0.99},
                {"word": "and", "start": 0.6, "end": 0.8, "probability": 0.98},
                {"word": "welcome", "start": 0.9, "end": 1.3, "probability": 0.97},
                {"word": "to", "start": 1.4, "end": 1.5, "probability": 0.99},
                {"word": "this", "start": 1.6, "end": 1.8, "probability": 0.98},
                {"word": "video", "start": 1.9, "end": 2.3, "probability": 0.99},
            ],
        },
        {
            "start": 5.5,
            "end": 10.0,
            "text": "Today we are going to discuss something amazing",
            "words": [
                {"word": "Today", "start": 5.5, "end": 5.9, "probability": 0.98},
                {"word": "we", "start": 6.0, "end": 6.1, "probability": 0.99},
                {"word": "are", "start": 6.2, "end": 6.3, "probability": 0.98},
                {"word": "going", "start": 6.4, "end": 6.7, "probability": 0.97},
                {"word": "to", "start": 6.8, "end": 6.9, "probability": 0.99},
                {"word": "discuss", "start": 7.0, "end": 7.5, "probability": 0.96},
                {"word": "something", "start": 7.6, "end": 8.1, "probability": 0.95},
                {"word": "amazing", "start": 8.2, "end": 8.8, "probability": 0.97},
            ],
        },
    ]
