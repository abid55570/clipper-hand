"""Smart cropping with optional face detection for aspect ratio conversion."""
import subprocess
import json
import structlog

logger = structlog.get_logger(__name__)


def detect_faces_center(input_path: str) -> tuple[int, int] | None:
    """Detect face region center using OpenCV Haar cascades.

    Returns (center_x, center_y) of the primary face, or None.
    """
    try:
        import cv2
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            return None

        # Sample a frame from the middle of the video
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames // 2)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            return None

        # Use Haar cascade for face detection
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        face_cascade = cv2.CascadeClassifier(cascade_path)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) > 0:
            # Use the largest face
            largest = max(faces, key=lambda f: f[2] * f[3])
            x, y, w, h = largest
            center_x = x + w // 2
            center_y = y + h // 2
            logger.info("face_detected", center_x=center_x, center_y=center_y)
            return (center_x, center_y)

        return None
    except ImportError:
        logger.warning("opencv_not_available")
        return None
    except Exception as e:
        logger.warning("face_detection_failed", error=str(e))
        return None


def calculate_smart_crop(
    src_width: int, src_height: int,
    target_width: int, target_height: int,
    face_center: tuple[int, int] | None = None,
) -> dict:
    """Calculate optimal crop region for aspect ratio conversion.

    Returns crop parameters {x, y, w, h} for ffmpeg crop filter.
    """
    target_ratio = target_width / target_height
    src_ratio = src_width / src_height

    if abs(src_ratio - target_ratio) < 0.01:
        # Already the right ratio
        return {"x": 0, "y": 0, "w": src_width, "h": src_height}

    if src_ratio > target_ratio:
        # Source is wider than target - crop width
        crop_h = src_height
        crop_w = int(src_height * target_ratio)
        crop_y = 0

        if face_center:
            # Center crop on face
            crop_x = max(0, min(face_center[0] - crop_w // 2, src_width - crop_w))
        else:
            # Center crop
            crop_x = (src_width - crop_w) // 2
    else:
        # Source is taller than target - crop height
        crop_w = src_width
        crop_h = int(src_width / target_ratio)
        crop_x = 0

        if face_center:
            crop_y = max(0, min(face_center[1] - crop_h // 2, src_height - crop_h))
        else:
            crop_y = (src_height - crop_h) // 2

    return {"x": crop_x, "y": crop_y, "w": crop_w, "h": crop_h}


def smart_crop_video(input_path: str, output_path: str,
                     target_width: int, target_height: int) -> str:
    """Crop and resize video using face detection for optimal framing."""
    from worker.processors.ffmpeg_wrapper import probe, resize_video

    # Get source dimensions
    probe_data = probe(input_path)
    video_stream = next((s for s in probe_data.get("streams", []) if s["codec_type"] == "video"), None)
    if not video_stream:
        raise RuntimeError("No video stream found")

    src_w = int(video_stream["width"])
    src_h = int(video_stream["height"])

    # Detect face center
    face_center = detect_faces_center(input_path)

    # Calculate crop region
    crop = calculate_smart_crop(src_w, src_h, target_width, target_height, face_center)

    # Apply crop and resize
    resize_video(
        input_path, target_width, target_height, output_path,
        crop_x=crop["x"], crop_y=crop["y"],
        crop_w=crop["w"], crop_h=crop["h"],
    )

    logger.info("smart_crop_applied", crop=crop, face_detected=face_center is not None)
    return output_path
