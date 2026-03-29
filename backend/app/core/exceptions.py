from fastapi import HTTPException, status


class AppError(Exception):
    """Base application error."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class VideoNotFoundError(AppError):
    def __init__(self, video_id: str):
        super().__init__(f"Video not found: {video_id}", status_code=404)


class ClipNotFoundError(AppError):
    def __init__(self, clip_id: str):
        super().__init__(f"Clip not found: {clip_id}", status_code=404)


class JobNotFoundError(AppError):
    def __init__(self, job_id: str):
        super().__init__(f"Job not found: {job_id}", status_code=404)


class ExportNotFoundError(AppError):
    def __init__(self, export_id: str):
        super().__init__(f"Export not found: {export_id}", status_code=404)


class CaptionNotFoundError(AppError):
    def __init__(self, caption_id: str):
        super().__init__(f"Caption not found: {caption_id}", status_code=404)


class InvalidFileError(AppError):
    def __init__(self, message: str = "Invalid file type"):
        super().__init__(message, status_code=400)


class FileTooLargeError(AppError):
    def __init__(self, max_size_gb: float):
        super().__init__(f"File exceeds maximum size of {max_size_gb} GB", status_code=413)


class ClipExtractionError(AppError):
    def __init__(self, message: str = "Failed to extract clip"):
        super().__init__(message, status_code=500)


class TranscriptionError(AppError):
    def __init__(self, message: str = "Transcription failed"):
        super().__init__(message, status_code=500)


class UploadNotFoundError(AppError):
    def __init__(self, upload_id: str):
        super().__init__(f"Upload session not found: {upload_id}", status_code=404)


class InvalidTimestampError(AppError):
    def __init__(self, message: str = "Invalid timestamp range"):
        super().__init__(message, status_code=400)
