import os
from typing import Generator, Any
from faster_whisper import WhisperModel
from backend.services.logger import logger
from backend.services.config_mgr import config_mgr

class FasterWhisperService:
    """
    Service for transcribing audio/video files using Faster-Whisper.
    Faster-Whisper uses PyAV (FFmpeg libraries) internally, so external
    FFmpeg binaries are not strictly required for the Python API.
    """

    def __init__(self) -> None:
        self.model: Any = None
        self._current_model_size: str = ""

    def _ensure_model_loaded(self) -> None:
        """
        Loads the model if it's not already loaded or if the size has changed.
        Includes a fallback to CPU if CUDA initialization fails.
        """
        config = config_mgr.config.whisper
        if self.model is None or self._current_model_size != config.model_size:
            logger.info(f"loading_whisper_model: {config.model_size} on {config.device}")
            
            # Auto-detect compute type if not specified
            compute_type = config.compute_type
            if compute_type == "default":
                compute_type = "float16" if config.device == "cuda" else "int8"

            try:
                self.model = WhisperModel(
                    config.model_size,
                    device=config.device,
                    compute_type=compute_type
                )
            except Exception as e:
                if config.device == "cuda":
                    logger.warning(f"cuda_init_failed_falling_back_to_cpu: {e}")
                    # Force CPU fallback
                    self.model = WhisperModel(
                        config.model_size,
                        device="cpu",
                        compute_type="int8"
                    )
                else:
                    logger.error(f"whisper_model_load_failed: {e}")
                    raise e

            self._current_model_size = config.model_size
            logger.info(f"whisper_model_loaded_successfully: {config.model_size} on {self.model.model.device}")

    def transcribe(self, media_path: str) -> Generator[dict, None, None]:
        """
        Transcribes an audio or video file and yields segments.

        Args:
            media_path (str): Path to the media file.

        Yields:
            dict: A segment with start, end, and text.
        """
        self._ensure_model_loaded()
        
        config = config_mgr.config.whisper
        logger.info(f"transcription_started: {media_path}")

        # Faster-whisper handles video paths directly via PyAV
        segments, info = self.model.transcribe(
            media_path,
            beam_size=5,
            language=config.language,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
        )

        logger.info(f"detected_language: {info.language} with probability {info.language_probability}")

        for segment in segments:
            yield {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip()
            }
        
        logger.info("transcription_completed")

# Global whisper service instance
whisper_svc = FasterWhisperService()
