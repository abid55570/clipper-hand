"""Whisper speech-to-text wrapper with word-level timestamps."""
import os
import structlog

logger = structlog.get_logger(__name__)

_model_cache = {}


def load_model(model_size: str = "base"):
    """Load Whisper model with caching."""
    if model_size in _model_cache:
        return _model_cache[model_size]

    try:
        import whisper
        logger.info("loading_whisper_model", model_size=model_size)
        model = whisper.load_model(model_size)
        _model_cache[model_size] = model
        return model
    except ImportError:
        logger.error("whisper_not_installed")
        raise RuntimeError("OpenAI Whisper is not installed")


def transcribe(audio_path: str, model_size: str = "base") -> dict:
    """Transcribe audio file with word-level timestamps.

    Returns:
        {
            "text": "full transcript...",
            "language": "en",
            "segments": [
                {
                    "start": 0.0,
                    "end": 5.2,
                    "text": "Hello world",
                    "words": [
                        {"word": "Hello", "start": 0.0, "end": 0.5, "probability": 0.99},
                        {"word": "world", "start": 0.6, "end": 1.0, "probability": 0.98},
                    ]
                },
                ...
            ]
        }
    """
    model = load_model(model_size)

    logger.info("transcribing", audio_path=audio_path, model_size=model_size)
    result = model.transcribe(
        audio_path,
        word_timestamps=True,
        verbose=False,
    )

    segments = []
    for seg in result.get("segments", []):
        words = []
        for w in seg.get("words", []):
            words.append({
                "word": w.get("word", "").strip(),
                "start": round(w.get("start", 0), 3),
                "end": round(w.get("end", 0), 3),
                "probability": round(w.get("probability", 0), 4),
            })
        segments.append({
            "start": round(seg.get("start", 0), 3),
            "end": round(seg.get("end", 0), 3),
            "text": seg.get("text", "").strip(),
            "words": words,
        })

    return {
        "text": result.get("text", "").strip(),
        "language": result.get("language", "unknown"),
        "segments": segments,
    }
