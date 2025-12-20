import threading
import os
import time
from typing import Optional
import webview
from backend.services.logger import logger
from backend.services.config_mgr import config_mgr
from backend.core.audio_proc import extract_audio
from backend.core.whisper_svc import whisper_svc
from backend.core.ai_engine import ai_engine

class ApiBridge:
    """
    Bridge class for communication between Javascript and Python.
    Methods in this class are accessible from JS via window.pywebview.api.
    """

    def __init__(self) -> None:
        self.window: Optional[webview.Window] = None
        self._is_processing: bool = False

    def set_window(self, window: webview.Window) -> None:
        """
        Sets the webview window instance.
        """
        self.window = window

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
        if not self.window:
            return None
        
        file_types = ("Video files (*.mp4;*.mkv;*.avi)", "All files (*.*)")
        result = self.window.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False, file_types=file_types)
        return result[0] if result else None

    def minimize(self) -> None:
        """Minimizes the window."""
        if self.window:
            self.window.minimize()

    def close(self) -> None:
        """Closes the window."""
        if self.window:
            self.window.destroy()

    def get_position(self) -> dict:
        """Returns current window position."""
        if self.window:
            return {"x": self.window.x, "y": self.window.y}
        return {"x": 0, "y": 0}

    def move_window(self, x: int, y: int) -> None:
        """Moves the window to coordinates."""
        if self.window:
            self.window.move(x, y)

    def start_task(self, video_path: str, target_lang: str = "Chinese") -> dict:
        """
        Starts the subtitle generation process in a separate thread.
        """
        if self._is_processing:
            return {"status": "error", "message": "A task is already running."}

        if not os.path.exists(video_path):
            return {"status": "error", "message": "File not found."}

        self._is_processing = True
        threading.Thread(target=self._run_task, args=(video_path, target_lang), daemon=True).start()
        return {"status": "started"}

    def _run_task(self, video_path: str, target_lang: str) -> None:
        """
        Inner method to run the transcription and translation flow.
        """
        try:
            self._notify_frontend("status_update", {"message": "Extracting audio...", "progress": 5})
            
            # 1. Extract Audio
            audio_path = video_path + ".temp.wav"
            if not extract_audio(video_path, audio_path):
                self._notify_frontend("task_failed", {"message": "Failed to extract audio."})
                return

            self._notify_frontend("status_update", {"message": "Transcribing...", "progress": 20})

            # 2. Transcribe
            segments = []
            for segment in whisper_svc.transcribe(audio_path):
                segments.append(segment)
                # Periodic progress update (simplified)
                progress = min(20 + len(segments), 60)
                self._notify_frontend("status_update", {"message": f"Transcribed {len(segments)} segments...", "progress": progress})

            self._notify_frontend("status_update", {"message": "Translating...", "progress": 70})

            # 3. Translate in batches
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

            # 4. Generate SRT or send back to frontend
            self._notify_frontend("task_completed", {"segments": results})

            # Cleanup
            if os.path.exists(audio_path):
                os.remove(audio_path)

        except Exception as e:
            logger.error(f"task_execution_failed: {e}", exc_info=True)
            self._notify_frontend("task_failed", {"message": str(e)})
        finally:
            self._is_processing = False

    def _notify_frontend(self, event_name: str, data: dict) -> None:
        """
        Sends an event notification to the frontend via JS.
        """
        if self.window:
            # We assume a global function 'onBackendEvent' exists in JS
            import json
            payload = json.dumps(data)
            self.window.evaluate_js(f"window.onBackendEvent('{event_name}', {payload})")
