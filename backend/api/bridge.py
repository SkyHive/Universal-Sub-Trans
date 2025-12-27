import threading
import os
import time
from typing import Optional
import webview
from backend.services.logger import logger
from backend.services.config_mgr import config_mgr
from backend.core.whisper_svc import whisper_svc
from backend.core.ai_engine import ai_engine
from backend.core.srt_utils import save_srt

class ApiBridge:
    """
    Bridge class for communication between Javascript and Python.
    Methods in this class are accessible from JS via window.pywebview.api.
    """

    def __init__(self) -> None:
        self._window: Optional[webview.Window] = None
        self._is_processing: bool = False

    def set_window(self, window: webview.Window) -> None:
        """
        Sets the webview window instance.
        """
        self._window = window

    def check_dep_status(self) -> dict:
        """
        Checks if hardware is NVIDIA and if dependencies are missing.
        """
        from backend.services.hardware_mgr import hardware_mgr
        from backend.services.dep_mgr import dep_mgr
        
        vendor = hardware_mgr.detect_gpu_vendor()
        return {
            "gpu_vendor": vendor,
            "can_accelerate": vendor == "nvidia",
            "needs_install": vendor == "nvidia" and dep_mgr.check_missing_deps()
        }

    def install_deps(self) -> dict:
        """
        Triggers the download and installation of dependencies.
        """
        from backend.services.dep_mgr import dep_mgr
        
        def _on_progress(progress: float):
            self._notify_frontend("dep_install_progress", {"progress": progress})

        def _run_install():
            success = dep_mgr.download_deps(progress_callback=_on_progress)
            if success:
                self._notify_frontend("dep_install_completed", {"message": "Installation successful. Please restart application to enable GPU."})
            else:
                self._notify_frontend("dep_install_failed", {"message": "Download failed. Check your internet connection."})

        threading.Thread(target=_run_install, daemon=True).start()
        return {"status": "started"}

    def get_config(self) -> dict:
        """
        Returns the current configuration as a dictionary.
        """
        logger.info("backend_get_config_called")
        return config_mgr.config.model_dump()

    def update_config(self, updates: dict) -> dict:
        """
        Updates the application configuration.
        """
        config_mgr.update_config(updates)
        return {"status": "success", "config": config_mgr.config.model_dump()}

    def select_file(self) -> Optional[str]:
        """
        Opens a file selection dialog.
        """
        if not self._window:
            return None
        
        file_types = ("Video files (*.mp4;*.mkv;*.avi)", "All files (*.*)")
        result = self._window.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False, file_types=file_types)
        return result[0] if result else None

    def minimize(self) -> None:
        """Minimizes the window."""
        if self._window:
            self._window.minimize()

    def close(self) -> None:
        """Closes the window."""
        if self._window:
            self._window.destroy()

    def get_position(self) -> dict:
        """Returns current window position."""
        if self._window:
            return {"x": self._window.x, "y": self._window.y}
        return {"x": 0, "y": 0}

    def move_window(self, x: int, y: int) -> None:
        """Moves the window to coordinates."""
        if self._window:
            self._window.move(x, y)

    def get_size(self) -> dict:
        """Returns current window size."""
        if self._window:
            return {"width": self._window.width, "height": self._window.height}
        return {"width": 0, "height": 0}

    def resize_window(self, width: int, height: int) -> None:
        """Resizes the window."""
        if self._window:
            self._window.resize(width, height)

    def check_task_resume_point(self, video_path: str) -> dict:
        """
        Detects if temporary audio or transcript files exist for the given video.
        """
        audio_path = video_path + ".temp.wav"
        transcript_path = video_path + ".temp.json"
        
        return {
            "has_audio": os.path.exists(audio_path),
            "has_transcript": os.path.exists(transcript_path)
        }

    def start_task(self, video_path: str, target_lang: str = "Chinese", resume_mode: str = "fresh") -> dict:
        """
        Starts the subtitle generation process. 
        resume_mode: 'fresh', 'use_audio', 'use_transcript'
        """
        if self._is_processing:
            return {"status": "error", "message": "A task is already running."}

        if not os.path.exists(video_path):
            return {"status": "error", "message": "File not found."}

        self._is_processing = True
        threading.Thread(target=self._run_task, args=(video_path, target_lang, resume_mode), daemon=True).start()
        return {"status": "started"}

    def _run_task(self, video_path: str, target_lang: str, resume_mode: str) -> None:
        """
        Inner method to run the transcription and translation flow with resume support.
        """
        try:
            audio_path = video_path + ".temp.wav"
            transcript_path = video_path + ".temp.json"
            segments = []

            # --- STEP 1: Transcription ---
            if resume_mode == "use_transcript" and os.path.exists(transcript_path):
                logger.info("resuming_from_transcript_cache")
                self._notify_frontend("status_update", {"message": "Loading saved transcript...", "progress": 25})
                import json
                with open(transcript_path, 'r', encoding='utf-8') as f:
                    segments = json.load(f)
            else:
                self._notify_frontend("status_update", {"message": "Transcribing...", "progress": 20})
                # Directly transcribe the video file
                input_media = audio_path if (resume_mode == "use_audio" and os.path.exists(audio_path)) else video_path
                for segment in whisper_svc.transcribe(input_media):
                    segments.append(segment)
                    progress = min(20 + len(segments), 60)
                    self._notify_frontend("status_update", {"message": f"Transcribed {len(segments)} segments...", "progress": progress})
                
                # Save checkpoint for source segments
                try:
                    import json
                    with open(transcript_path, 'w', encoding='utf-8') as f:
                        json.dump(segments, f, ensure_ascii=False, indent=2)
                    logger.info("transcript_checkpoint_saved")
                except Exception as ex:
                    logger.error(f"failed_to_save_checkpoint: {ex}")

            # --- STEP 3: Translation ---
            self._notify_frontend("status_update", {"message": "Translating...", "progress": 70})
            batch_size = config_mgr.config.ai.batch_size
            results = []
            
            for i in range(0, len(segments), batch_size):
                batch = segments[i:i + batch_size]
                texts = [s["text"] for s in batch]
                translations = ai_engine.translate_batch(texts, target_lang)
                
                for j, trans in enumerate(translations):
                    if j < len(batch):
                        batch[j]["translated_text"] = trans
                
                results.extend(batch)
                progress = 70 + int((i / len(segments)) * 25)
                self._notify_frontend("status_update", {"message": f"Translated {len(results)}/{len(segments)}...", "progress": progress})

            # --- STEP 4: Save SRT ---
            self._notify_frontend("status_update", {"message": "Saving SRT file...", "progress": 95})
            
            # Generate SRT path: video.mp4 -> video.srt or video.zh.srt
            base_path = os.path.splitext(video_path)[0]
            # Use a language suffix if possible, or just .srt
            srt_path = f"{base_path}.srt"
            
            try:
                save_srt(results, srt_path)
                logger.info(f"srt_saved_successfully: {srt_path}")
            except Exception as se:
                logger.error(f"failed_to_save_srt: {se}")
                # We don't fail the whole task if just saving fails, 
                # but we should probably notify the user.

            # 5. Finalize
            self._notify_frontend("task_completed", {"segments": results, "srt_path": srt_path})

            # Cleanup audio only if not intended to keep it (optional)
            # We keep transcript_path (.temp.json) for future resumes unless user manually clears it
            # if os.path.exists(audio_path): os.remove(audio_path)

        except Exception as e:
            logger.error(f"task_execution_failed: {e}", exc_info=True)
            self._notify_frontend("task_failed", {"message": str(e)})
        finally:
            self._is_processing = False

    def _notify_frontend(self, event_name: str, data: dict) -> None:
        """
        Sends an event notification to the frontend via JS.
        """
        if self._window:
            # We assume a global function 'onBackendEvent' exists in JS
            import json
            payload = json.dumps(data)
            self._window.evaluate_js(f"window.onBackendEvent('{event_name}', {payload})")
