import os
import platform
import subprocess
from typing import Optional
from backend.services.logger import logger
from backend.services.config_mgr import config_mgr

def get_ffmpeg_path() -> str:
    """
    Determines the path to the ffmpeg binary based on platform and config.

    Returns:
        str: Path to the ffmpeg binary.
    """
    # Check if manually configured
    if config_mgr.config.app.ffmpeg_path and os.path.exists(config_mgr.config.app.ffmpeg_path):
        return config_mgr.config.app.ffmpeg_path

    # Check in bin/platform directory
    curr_os = platform.system().lower()
    ext = ".exe" if curr_os == "windows" else ""
    bin_path = os.path.join(os.getcwd(), "bin", curr_os, f"ffmpeg{ext}")

    if os.path.exists(bin_path):
        return bin_path

    # Fallback to system ffmpeg
    return "ffmpeg"

def extract_audio(video_path: str, audio_output_path: str) -> bool:
    """
    Extracts audio from a video file using FFmpeg.

    Args:
        video_path (str): Path to the source video file.
        audio_output_path (str): Path where the audio file will be saved.

    Returns:
        bool: True if successful, False otherwise.
    """
    ffmpeg_path = get_ffmpeg_path()
    
    cmd = [
        ffmpeg_path,
        "-y",               # Overwrite output files
        "-i", video_path,
        "-vn",              # Disable video
        "-acodec", "pcm_s16le", # 16-bit PCM
        "-ar", "16000",     # 16kHz sample rate (Whisper standard)
        "-ac", "1",          # Mono
        audio_output_path
    ]

    logger.info(f"extracting_audio_started: {video_path}")
    try:
        # Using subprocess.run for blocking call (should be run in a thread by caller)
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=True
        )
        logger.info(f"extract_audio_success: {audio_output_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"extract_audio_failed: {e.stderr}", extra={"stderr": e.stderr})
        return False
    except Exception as e:
        logger.error(f"extract_audio_unexpected_error: {e}", exc_info=True)
        return False
