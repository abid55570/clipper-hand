"""AI-powered video analysis for highlight detection and content generation."""
import os
import numpy as np
import structlog

logger = structlog.get_logger(__name__)


def detect_audio_energy_peaks(audio_path: str, top_n: int = 10,
                               min_duration: float = 15.0,
                               window_sec: float = 5.0) -> list[dict]:
    """Detect high-energy audio segments (potential highlights).

    Uses librosa for audio analysis to find peaks in RMS energy.
    """
    try:
        import librosa
    except ImportError:
        logger.warning("librosa_not_available")
        return []

    logger.info("analyzing_audio_energy", audio_path=audio_path)
    y, sr = librosa.load(audio_path, sr=22050)
    duration = librosa.get_duration(y=y, sr=sr)

    # Compute RMS energy in windows
    hop_length = int(sr * 0.5)  # 0.5 second hops
    rms = librosa.feature.rms(y=y, frame_length=int(sr * window_sec), hop_length=hop_length)[0]
    times = librosa.frames_to_time(range(len(rms)), sr=sr, hop_length=hop_length)

    # Normalize RMS
    if rms.max() > 0:
        rms_normalized = rms / rms.max()
    else:
        return []

    # Find peaks above 75th percentile
    threshold = np.percentile(rms_normalized, 75)
    peak_indices = np.where(rms_normalized > threshold)[0]

    # Group adjacent peaks into segments
    highlights = []
    if len(peak_indices) == 0:
        return []

    seg_start = times[peak_indices[0]]
    seg_end = seg_start
    prev_idx = peak_indices[0]

    for idx in peak_indices[1:]:
        if idx - prev_idx <= 2:  # Adjacent or close
            seg_end = times[idx]
        else:
            # End of segment
            if seg_end - seg_start >= 1.0:  # Min 1 second
                # Extend to min_duration
                center = (seg_start + seg_end) / 2
                hl_start = max(0, center - min_duration / 2)
                hl_end = min(duration, center + min_duration / 2)
                avg_energy = float(np.mean(rms_normalized[peak_indices[0]:idx]))
                highlights.append({
                    "start_time": round(hl_start, 2),
                    "end_time": round(hl_end, 2),
                    "score": round(avg_energy, 4),
                    "reason": "High audio energy detected",
                    "source": "audio_energy",
                })
            seg_start = times[idx]
            seg_end = seg_start
        prev_idx = idx

    # Handle last segment
    if seg_end - seg_start >= 1.0:
        center = (seg_start + seg_end) / 2
        hl_start = max(0, center - min_duration / 2)
        hl_end = min(duration, center + min_duration / 2)
        highlights.append({
            "start_time": round(hl_start, 2),
            "end_time": round(hl_end, 2),
            "score": round(float(np.mean(rms_normalized[-len(peak_indices):])), 4),
            "reason": "High audio energy detected",
            "source": "audio_energy",
        })

    # Sort by score and return top N
    highlights.sort(key=lambda x: x["score"], reverse=True)
    return highlights[:top_n]


def detect_scene_highlights(scene_timestamps: list[float], duration: float,
                            min_duration: float = 15.0, top_n: int = 5) -> list[dict]:
    """Convert scene change timestamps into highlight suggestions."""
    if len(scene_timestamps) < 2:
        return []

    highlights = []
    # Find segments with dense scene changes (high activity)
    window = 30.0  # 30-second windows
    for start in np.arange(0, duration - window, window / 2):
        end = start + window
        changes_in_window = sum(1 for t in scene_timestamps if start <= t <= end)
        if changes_in_window >= 3:  # At least 3 scene changes
            score = min(changes_in_window / 10.0, 1.0)
            highlights.append({
                "start_time": round(float(start), 2),
                "end_time": round(float(min(end, duration)), 2),
                "score": round(score, 4),
                "reason": f"{changes_in_window} scene changes detected",
                "source": "scene_change",
            })

    highlights.sort(key=lambda x: x["score"], reverse=True)
    return highlights[:top_n]


def generate_content_from_transcript(transcript: str, clip_duration: float = 0) -> dict:
    """Generate title, description, and hashtags from transcript text.

    Uses simple heuristic-based approach. Can be enhanced with LLM API.
    """
    words = transcript.split()
    sentences = [s.strip() for s in transcript.replace("!", ".").replace("?", ".").split(".") if s.strip()]

    # Title: first meaningful sentence (or first 10 words)
    title = sentences[0] if sentences else " ".join(words[:10])
    if len(title) > 80:
        title = title[:77] + "..."

    # Description: first 2-3 sentences
    desc_sentences = sentences[:3] if len(sentences) >= 3 else sentences
    description = ". ".join(desc_sentences) + "." if desc_sentences else transcript[:200]

    # Hashtags: most common significant words
    stop_words = {"the", "a", "an", "is", "are", "was", "were", "in", "on", "at", "to", "for",
                  "of", "and", "or", "but", "not", "this", "that", "it", "i", "you", "we",
                  "they", "he", "she", "my", "your", "his", "her", "its", "with", "from"}
    word_freq = {}
    for word in words:
        clean = word.strip(".,!?;:\"'()[]").lower()
        if len(clean) > 3 and clean not in stop_words:
            word_freq[clean] = word_freq.get(clean, 0) + 1

    top_words = sorted(word_freq, key=word_freq.get, reverse=True)[:8]
    hashtags = [f"#{w}" for w in top_words]

    # Add generic content hashtags
    hashtags.extend(["#content", "#viral", "#clips"])

    return {
        "title": title,
        "description": description,
        "hashtags": hashtags[:10],
    }


def generate_hooks(transcript: str) -> list[dict]:
    """Generate engaging hook/intro text suggestions."""
    sentences = [s.strip() for s in transcript.replace("!", ".").replace("?", ".").split(".") if s.strip()]

    hooks = []

    # Hook 1: Question-based
    if sentences:
        hooks.append({
            "text": f"Did you know? {sentences[0]}",
            "style": "bold",
        })

    # Hook 2: Bold statement
    if len(sentences) > 1:
        hooks.append({
            "text": f"🔥 {sentences[1]}",
            "style": "pop",
        })

    # Hook 3: "Wait for it" style
    hooks.append({
        "text": "You won't believe what happens next...",
        "style": "slide",
    })

    # Hook 4: Direct engagement
    if sentences:
        first_words = " ".join(sentences[0].split()[:5])
        hooks.append({
            "text": f"Listen to this: {first_words}...",
            "style": "fade",
        })

    return hooks
