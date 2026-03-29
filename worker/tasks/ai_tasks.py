"""Celery tasks for AI-powered video analysis."""
import os
import uuid
import tempfile
from celery.exceptions import SoftTimeLimitExceeded
from worker.app import celery_app
from worker.processors import ffmpeg_wrapper, ai_analyzer
import structlog

logger = structlog.get_logger(__name__)


def _get_db_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine(
        os.environ.get("DATABASE_URL_SYNC", "postgresql://clipper:clipper_pass@postgres:5432/clipper_db"),
        pool_pre_ping=True,
    )
    return sessionmaker(bind=engine)()


def _update_job(session, job_id: str, **kwargs):
    from app.models.job import Job
    job = session.query(Job).filter(Job.id == uuid.UUID(job_id)).first()
    if job:
        for k, v in kwargs.items():
            setattr(job, k, v)
        session.commit()


@celery_app.task(bind=True, name="worker.tasks.ai_tasks.detect_highlights",
                 max_retries=2, default_retry_delay=120)
def detect_highlights(self, job_id: str, video_id: str):
    """Detect highlights in a video using audio energy and scene analysis."""
    session = _get_db_session()
    try:
        _update_job(session, job_id, status="running", progress_pct=5)

        from app.models.video import Video
        from app.models.export import Highlight

        video = session.query(Video).filter(Video.id == uuid.UUID(video_id)).first()
        if not video:
            _update_job(session, job_id, status="failed", error_message="Video not found")
            return

        audio_path = tempfile.mktemp(suffix=".wav")
        try:
            # Extract audio for analysis
            ffmpeg_wrapper.extract_audio(video.file_path, audio_path)
            _update_job(session, job_id, progress_pct=20)

            # Detect audio energy peaks
            audio_highlights = ai_analyzer.detect_audio_energy_peaks(audio_path)
            _update_job(session, job_id, progress_pct=50)

            # Detect scene changes
            scene_timestamps = ffmpeg_wrapper.detect_scene_changes(video.file_path)
            scene_highlights = ai_analyzer.detect_scene_highlights(
                scene_timestamps, video.duration_secs or 0
            )
            _update_job(session, job_id, progress_pct=80)

            # Combine and deduplicate highlights
            all_highlights = audio_highlights + scene_highlights
            all_highlights.sort(key=lambda h: h["score"], reverse=True)

            # Save to database
            for h in all_highlights[:15]:  # Keep top 15
                highlight = Highlight(
                    video_id=uuid.UUID(video_id),
                    start_time=h["start_time"],
                    end_time=h["end_time"],
                    score=h["score"],
                    reason=h["reason"],
                    source=h["source"],
                )
                session.add(highlight)
            session.commit()

            _update_job(session, job_id, status="completed", progress_pct=100,
                        result_json={"highlights_count": len(all_highlights)})
            logger.info("highlights_detected", video_id=video_id, count=len(all_highlights))

        finally:
            if os.path.exists(audio_path):
                os.unlink(audio_path)

    except SoftTimeLimitExceeded:
        _update_job(session, job_id, status="failed", error_message="Task timed out")
    except Exception as exc:
        _update_job(session, job_id, status="failed", error_message=str(exc))
        raise self.retry(exc=exc)
    finally:
        session.close()


@celery_app.task(bind=True, name="worker.tasks.ai_tasks.generate_content",
                 max_retries=2, default_retry_delay=30)
def generate_content(self, job_id: str, clip_id: str):
    """Generate title, description, and hashtags for a clip."""
    session = _get_db_session()
    try:
        _update_job(session, job_id, status="running", progress_pct=10)

        from app.models.clip import Clip
        from app.models.caption import Caption, CaptionSegment

        clip = session.query(Clip).filter(Clip.id == uuid.UUID(clip_id)).first()
        if not clip:
            _update_job(session, job_id, status="failed", error_message="Clip not found")
            return

        # Try to get transcript for this clip's time range
        transcript = ""
        captions = session.query(Caption).filter(
            Caption.video_id == clip.video_id, Caption.status == "ready"
        ).first()

        if captions:
            segments = session.query(CaptionSegment).filter(
                CaptionSegment.caption_id == captions.id,
            ).order_by(CaptionSegment.segment_index).all()

            for seg in segments:
                if seg.end_time > clip.start_time and seg.start_time < clip.end_time:
                    transcript += seg.text + " "

        if not transcript.strip():
            transcript = f"Video clip from {clip.start_time}s to {clip.end_time}s"

        _update_job(session, job_id, progress_pct=50)

        content = ai_analyzer.generate_content_from_transcript(
            transcript.strip(), clip.duration_secs or 0
        )

        _update_job(session, job_id, status="completed", progress_pct=100,
                    result_json=content)
        logger.info("content_generated", clip_id=clip_id)

    except Exception as exc:
        _update_job(session, job_id, status="failed", error_message=str(exc))
        raise self.retry(exc=exc)
    finally:
        session.close()


@celery_app.task(bind=True, name="worker.tasks.ai_tasks.generate_hooks",
                 max_retries=2, default_retry_delay=30)
def generate_hooks(self, job_id: str, clip_id: str):
    """Generate hook text suggestions for a clip."""
    session = _get_db_session()
    try:
        _update_job(session, job_id, status="running", progress_pct=10)

        from app.models.clip import Clip
        from app.models.caption import Caption, CaptionSegment

        clip = session.query(Clip).filter(Clip.id == uuid.UUID(clip_id)).first()
        if not clip:
            _update_job(session, job_id, status="failed", error_message="Clip not found")
            return

        transcript = ""
        captions = session.query(Caption).filter(
            Caption.video_id == clip.video_id, Caption.status == "ready"
        ).first()

        if captions:
            segments = session.query(CaptionSegment).filter(
                CaptionSegment.caption_id == captions.id,
            ).order_by(CaptionSegment.segment_index).all()
            for seg in segments:
                if seg.end_time > clip.start_time and seg.start_time < clip.end_time:
                    transcript += seg.text + " "

        if not transcript.strip():
            transcript = "An amazing video clip you need to see"

        hooks = ai_analyzer.generate_hooks(transcript.strip())

        _update_job(session, job_id, status="completed", progress_pct=100,
                    result_json={"hooks": hooks})
        logger.info("hooks_generated", clip_id=clip_id, count=len(hooks))

    except Exception as exc:
        _update_job(session, job_id, status="failed", error_message=str(exc))
        raise self.retry(exc=exc)
    finally:
        session.close()


@celery_app.task(bind=True, name="worker.tasks.ai_tasks.detect_speakers",
                 max_retries=1, default_retry_delay=60)
def detect_speakers(self, job_id: str, video_id: str):
    """Basic speaker detection placeholder."""
    session = _get_db_session()
    try:
        _update_job(session, job_id, status="running", progress_pct=10)

        from app.models.video import Video
        video = session.query(Video).filter(Video.id == uuid.UUID(video_id)).first()
        if not video:
            _update_job(session, job_id, status="failed", error_message="Video not found")
            return

        # Placeholder: simple voice activity detection
        # In production, use pyannote-audio or similar
        duration = video.duration_secs or 0
        speakers = [
            {
                "speaker_id": "speaker_1",
                "start_time": 0,
                "end_time": duration,
                "confidence": 0.5,
            }
        ]

        _update_job(session, job_id, status="completed", progress_pct=100,
                    result_json={"speakers": speakers,
                                 "note": "Placeholder detection - integrate pyannote-audio for production"})
        logger.info("speakers_detected", video_id=video_id)

    except Exception as exc:
        _update_job(session, job_id, status="failed", error_message=str(exc))
        raise self.retry(exc=exc)
    finally:
        session.close()
