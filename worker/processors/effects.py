"""Video effects: zoom, jump-cuts, text animations."""
from worker.processors import ffmpeg_wrapper
import structlog

logger = structlog.get_logger(__name__)


def apply_zoom_effect(input_path: str, output_path: str,
                      zoom_start: float = 0, zoom_duration: float = 3,
                      zoom_factor: float = 1.3) -> str:
    """Apply zoom-in effect."""
    return ffmpeg_wrapper.add_zoom_effect(
        input_path, output_path,
        zoom_start=zoom_start,
        zoom_duration=zoom_duration,
        zoom_factor=zoom_factor,
    )


def apply_jump_cuts(input_path: str, output_path: str,
                    threshold_db: float = -40.0,
                    min_silence: float = 0.5) -> str:
    """Remove silence from video (jump cut effect)."""
    return ffmpeg_wrapper.remove_silence(
        input_path, output_path,
        threshold_db=threshold_db,
        min_silence=min_silence,
    )


def apply_text_animation(input_path: str, output_path: str,
                         text: str, animation: str = "fade",
                         font_size: int = 48, position: str = "center",
                         start_time: float = 0, duration: float = 3) -> str:
    """Add animated text overlay."""
    return ffmpeg_wrapper.add_text_overlay(
        input_path, output_path,
        text=text, font_size=font_size,
        position=position,
        start_time=start_time,
        duration=duration,
        animation=animation,
    )


def apply_effects_chain(input_path: str, output_path: str,
                        effects_config: dict) -> str:
    """Apply a chain of effects to a video."""
    import tempfile
    from pathlib import Path

    current_input = input_path
    temp_files = []

    try:
        # 1. Jump cuts (silence removal)
        if effects_config.get("jump_cut"):
            temp_path = tempfile.mktemp(suffix=".mp4")
            temp_files.append(temp_path)
            apply_jump_cuts(
                current_input, temp_path,
                threshold_db=effects_config.get("jump_cut_threshold_db", -40.0),
                min_silence=effects_config.get("jump_cut_min_silence", 0.5),
            )
            current_input = temp_path

        # 2. Zoom effect
        if effects_config.get("zoom"):
            temp_path = tempfile.mktemp(suffix=".mp4")
            temp_files.append(temp_path)
            apply_zoom_effect(current_input, temp_path)
            current_input = temp_path

        # 3. Text animation
        if effects_config.get("text_animation") and effects_config.get("text_content"):
            temp_path = tempfile.mktemp(suffix=".mp4")
            temp_files.append(temp_path)
            apply_text_animation(
                current_input, temp_path,
                text=effects_config["text_content"],
                animation=effects_config.get("text_animation", "fade"),
            )
            current_input = temp_path

        # Copy final result to output
        if current_input != input_path:
            if current_input != output_path:
                Path(current_input).rename(output_path)
                # Remove it from temp_files since we renamed it
                if current_input in temp_files:
                    temp_files.remove(current_input)
        else:
            import shutil
            shutil.copy2(input_path, output_path)

    finally:
        for tf in temp_files:
            Path(tf).unlink(missing_ok=True)

    logger.info("effects_chain_applied", effects=list(effects_config.keys()), output=output_path)
    return output_path
