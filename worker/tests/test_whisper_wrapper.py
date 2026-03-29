"""Tests for Whisper wrapper (mocked - Whisper may not be available in test env)."""
import pytest
from unittest.mock import patch, MagicMock


class TestWhisperWrapper:
    def test_transcribe_mocked(self):
        """Test transcription with mocked Whisper model."""
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {
            "text": "Hello world. This is a test.",
            "language": "en",
            "segments": [
                {
                    "start": 0.0,
                    "end": 2.0,
                    "text": "Hello world.",
                    "words": [
                        {"word": "Hello", "start": 0.0, "end": 0.5, "probability": 0.99},
                        {"word": "world.", "start": 0.6, "end": 1.0, "probability": 0.98},
                    ],
                },
            ],
        }

        with patch("worker.processors.whisper_wrapper.load_model", return_value=mock_model):
            from worker.processors.whisper_wrapper import transcribe
            result = transcribe("/dummy/audio.wav", "base")

        assert result["text"] == "Hello world. This is a test."
        assert result["language"] == "en"
        assert len(result["segments"]) == 1
        assert len(result["segments"][0]["words"]) == 2
