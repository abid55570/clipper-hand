"""Celery tasks for transcription and subtitle processing."""
import os
import uuid
import tempfile
from celery.exceptions import SoftTimeLimitExceeded
from worker.app import celery_app
from worker.processors import ffmpeg_wrapper, whisper_wrapper, caption_renderer
import structlog

logger = structlog.get_logger(__name__)

MEDIA_DIR = os.environ.get("MEDIA_DIR", "/app/media")


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


@celery_app.task(bind=True, name="worker.tasks.caption_tasks.transcribe_video",
                 max_retries=2, default_retry_delay=120)
def transcribe_video(self, job_id: str, video_id: str, caption_id: str,
                      model_size: str = "base"):
    """Transcribe a video using Whisper."""
    session = _get_db_session()
    try:
        _update_job(session, job_id, status="running", progress_pct=5)

        from app.models.video import Video
        from app.models.caption import Caption, CaptionSegment
        video = session.query(Video).filter(Video.id == uuid.UUID(video_id)).first()
        if not video:
            _update_job(session, job_id, status="failed", error_message="Video not found")
            return

        # Extract audio
        audio_path = tempfile.mktemp(suffix=".wav")
        try:
            ffmpeg_wrapper.extract_audio(video.file_path, audio_path)
            _update_job(session, job_id, progress_pct=20)

            # Transcribe
            result = whisper_wrapper.transcribe(audio_path, model_size)
            _update_job(session, job_id, progress_pct=80)

            # Save results
            caption = session.query(Caption).filter(Caption.id == uuid.UUID(caption_id)).first()
            if caption:
                caption.full_text = result["text"]
                caption.language = result["language"]
                caption.status = "ready"

                # Save segments
                for i, seg in enumerate(result["segments"]):
                    segment = CaptionSegment(
                        caption_id=caption.id,
                        segment_index=i,
                        start_time=seg["start"],
                        end_time=seg["end"],
                        text=seg["text"],
                        words_json=seg.get("words"),
                    )
                    session.add(segment)

                session.commit()

            _update_job(session, job_id, status="completed", progress_pct=100,
                        result_json={"language": result["language"],
                                     "segments_count": len(result["segments"])})
            logger.info("transcription_completed", video_id=video_id,
                        segments=len(result["segments"]))

        finally:
            if os.path.exists(audio_path):
                os.unlink(audio_path)

    except SoftTimeLimitExceeded:
        _update_job(session, job_id, status="failed", error_message="Transcription timed out")
    except Exception as exc:
        _update_job(session, job_id, status="failed", error_message=str(exc))
        raise self.retry(exc=exc)
    finally:
        session.close()


@celery_app.task(bind=True, name="worker.tasks.caption_tasks.burn_subtitles",
                 max_retries=2, default_retry_delay=60)
def burn_subtitles(self, job_id: str, clip_id: str, caption_id: str,
                    style_data: dict | None = None):
    """Burn subtitles into a clip video."""
    session = _get_db_session()
    try:
        _update_job(session, job_id, status="running", progress_pct=10)

        from app.models.clip import Clip
        from app.models.caption import Caption, CaptionSegment, CaptionStyle

        clip = session.query(Clip).filter(Clip.id == uuid.UUID(clip_id)).first()
        if not clip or not clip.file_path:
            _update_job(session, job_id, status="failed", error_message="Clip not found or not ready")
            return

        caption = session.query(Caption).filter(Caption.id == uuid.UUID(caption_id)).first()
        if not caption:
            _update_job(session, job_id, status="failed", error_message="Caption not found")
            return

        # Get segments within clip time range
        segments = session.query(CaptionSegment).filter(
            CaptionSegment.caption_id == caption.id,
        ).order_by(CaptionSegment.segment_index).all()

        # Filter and adjust segments for clip time range
        clip_segments = []
        for seg in segments:
            if seg.end_time > clip.start_time and seg.start_time < clip.end_time:
                clip_segments.append({
                    "start": max(0, seg.start_time - clip.start_time),
                    "end": min(clip.end_time - clip.start_time, seg.end_time - clip.start_time),
                    "text": seg.text,
                    "words": seg.words_json or [],
                })

        if not clip_segments:
            _update_job(session, job_id, status="completed", progress_pct=100,
                        result_json={"message": "No captions in clip range"})
            return

        # Get style config
        if not style_data:
            style = session.query(CaptionStyle).filter(CaptionStyle.caption_id == caption.id).first()
            if style:
                style_data = {
                    "font_family": style.font_family,
                    "font_size": style.font_size,
                    "primary_color": style.primary_color,
                    "outline_color": style.outline_color,
                    "highlight_color": style.highlight_color,
                    "highlight_words": style.highlight_words or [],
                    "position": style.position,
                    "bold": style.bold,
                    "animation_type": style.animation_type,
                }

        _update_job(session, job_id, progress_pct=30)

        # Generate ASS subtitle
        ass_path = caption_renderer.generate_ass_subtitle(clip_segments, style_data)
        _update_job(session, job_id, progress_pct=50)

        # Burn subtitles
        os.makedirs(MEDIA_DIR, exist_ok=True)
        output_path = os.path.join(MEDIA_DIR, f"{uuid.uuid4().hex[:8]}_subtitled.mp4")
        ffmpeg_wrapper.burn_ass_subtitles(clip.file_path, ass_path, output_path)

        # Update clip
        file_size = os.path.getsize(output_path)
        clip.file_path = output_path
        clip.file_size_bytes = file_size
        session.commit()

        # Clean up ASS file
        os.unlink(ass_path)

        _update_job(session, job_id, status="completed", progress_pct=100)
        logger.info("subtitles_burned", clip_id=clip_id)

    except Exception as exc:
        _update_job(session, job_id, status="failed", error_message=str(exc))
        raise self.retry(exc=exc)
    finally:
        session.close()
