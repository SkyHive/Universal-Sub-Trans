import os
import platform
from typing import Generator, Any, Optional, Callable
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

    def _ensure_model_loaded(self, status_callback: Optional[Callable[[str], None]] = None) -> None:
        """
        Loads the model if it's not already loaded or if the size has changed.
        Includes a fallback to CPU if CUDA initialization fails.
        """
        config = config_mgr.config.whisper
        if self.model is None or self._current_model_size != config.model_size:
            msg = f"Loading AI Model ({config.model_size})..."
            logger.info(msg)
            if status_callback:
                status_callback(msg)
            
            # Auto-detect compute type if not specified
            compute_type = config.compute_type
            if compute_type == "default":
                compute_type = "float16" if config.device == "cuda" else "int8"

            try:
                # Debug info: print PATH and LD_LIBRARY_PATH if needed
                if platform.system().lower() == "windows":
                    logger.debug(f"current_path: {os.environ.get('PATH', '')[:200]}...")
                
                from faster_whisper import WhisperModel
                self.model = WhisperModel(
                    config.model_size,
                    device=config.device,
                    compute_type=compute_type
                )
            except ImportError as ie:
                logger.error(f"faster_whisper_import_failed: {ie}. Make sure faster-whisper is installed.")
                raise ie
            except Exception as e:
                if config.device == "cuda":
                    logger.warning(f"cuda_init_failed_falling_back_to_cpu: {e}")
                    # Force CPU fallback
                    try:
                        from faster_whisper import WhisperModel
                        self.model = WhisperModel(
                            config.model_size,
                            device="cpu",
                            compute_type="int8"
                        )
                    except Exception as cpu_e:
                        logger.error(f"whisper_cpu_fallback_failed: {cpu_e}")
                        raise cpu_e
                else:
                    logger.error(f"whisper_model_load_failed: {e}", exc_info=True)
                    raise e

            self._current_model_size = config.model_size
            logger.info(f"whisper_model_loaded_successfully: {config.model_size}")

    def transcribe(self, media_path: str, status_callback: Optional[Callable[[str, str], None]] = None) -> Generator[dict, None, None]:
        """
        Transcribes an audio or video file and yields segments.

        Args:
            media_path (str): Path to the media file.
            status_callback (Callable): Callback for status updates (e.g. model loading).

        Yields:
            dict: A segment with start, end, and text.
        """
        def _load_cb(msg: str):
            if status_callback:
                status_callback(msg, "loading_model")

        self._ensure_model_loaded(status_callback=_load_cb)
        
        if status_callback:
            status_callback("Model ready, starting transcription...", "transcribing")
        
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
