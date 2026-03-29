import os
import re
import uuid
from pathlib import Path
from app.config import settings
from app.core.exceptions import InvalidFileError, FileTooLargeError

ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpeg", ".mpg"}

ALLOWED_VIDEO_MIMETYPES = {
    "video/mp4",
    "video/x-msvideo",
    "video/x-matroska",
    "video/quicktime",
    "video/x-ms-wmv",
    "video/x-flv",
    "video/webm",
    "video/mpeg",
}

# Magic bytes for common video formats
VIDEO_MAGIC_BYTES = {
    b"\x00\x00\x00\x18ftypmp4": "mp4",
    b"\x00\x00\x00\x1cftyp": "mp4",
    b"\x00\x00\x00\x20ftyp": "mp4",
    b"\x1aE\xdf\xa3": "mkv/webm",
    b"RIFF": "avi",
    b"\x00\x00\x01\xba": "mpeg",
    b"\x00\x00\x01\xb3": "mpeg",
    b"FLV\x01": "flv",
}


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to prevent path traversal and other attacks."""
    # Remove any path components
    filename = os.path.basename(filename)
    # Remove non-alphanumeric characters except dots, hyphens, underscores
    filename = re.sub(r"[^\w\-.]", "_", filename)
    # Ensure filename is not empty
    if not filename or filename.startswith("."):
        filename = f"video_{uuid.uuid4().hex[:8]}{Path(filename).suffix if filename else '.mp4'}"
    return filename


def validate_video_extension(filename: str) -> None:
    """Validate that the file has an allowed video extension."""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise InvalidFileError(f"File extension '{ext}' is not allowed. Allowed: {', '.join(sorted(ALLOWED_VIDEO_EXTENSIONS))}")


def validate_file_size(size_bytes: int) -> None:
    """Validate that the file doesn't exceed the maximum upload size."""
    if size_bytes > settings.max_upload_size_bytes:
        raise FileTooLargeError(settings.max_upload_size_gb)


def validate_video_magic_bytes(header: bytes) -> None:
    """Validate file content by checking magic bytes."""
    for magic, fmt in VIDEO_MAGIC_BYTES.items():
        if header[:len(magic)] == magic:
            return
    # Also check for ftyp box anywhere in first 12 bytes (MP4/MOV variants)
    if b"ftyp" in header[:12]:
        return
    raise InvalidFileError("File content does not match any known video format")
