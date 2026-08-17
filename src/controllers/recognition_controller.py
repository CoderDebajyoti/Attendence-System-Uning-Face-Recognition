# ==============================================================================
# Face Recognition Attendance System - Face Recognition Controller
# ==============================================================================

import threading
import logging
from src.services.face_recognition_service import FaceRecognitionService
from src.services.student_service import StudentService

logger = logging.getLogger("app.system")

class RecognitionController:
    """
    Coordinates presentation logic and event handlers from the RecognitionPage GUI
    to the underlying FaceRecognitionService and StudentService layers.
    Also supports asynchronous, non-blocking model training.
    """

    def __init__(self) -> None:
        self.service = FaceRecognitionService.get_instance()
        self.student_service = StudentService()
        logger.info("RecognitionController initialized successfully.")

    def get_model_status(self) -> str:
        """
        Returns current model compilation status.
        """
        return self.service.get_model_status()

    def get_model_metadata(self) -> dict:
        """
        Returns the active model metadata.
        """
        return self.service.metadata

    def get_configured_threshold(self) -> float:
        """
        Returns the configured recognition similarity threshold.
        """
        return self.service.settings.recognition_threshold

    def is_camera_rtsp_configured(self) -> bool:
        """
        Checks if a custom RTSP stream url is configured.
        """
        return bool(self.service.settings.camera_rtsp_url)

    def get_camera_source(self) -> int | str:
        """
        Returns the configured camera ID or RTSP URL.
        """
        settings = self.service.settings
        return settings.camera_rtsp_url if settings.camera_rtsp_url else settings.camera_id

    def recognize_frame(self, frame, boxes: list[tuple[int, int, int, int]], threshold: float = None) -> list[dict]:
        """
        Performs recognition matching on detected face bounding boxes in a frame.
        """
        return self.service.recognize_frame(frame, boxes, threshold)

    def build_model_async(self, widget, on_complete_callback) -> None:
        """
        Launches the model building pipeline on a background daemon thread
        to prevent freezing the CustomTkinter UI event loop.
        Invokes the callback on the main Tk event thread once completed.
        """
        logger.info("Spawning background thread for model compilation...")
        
        def worker():
            try:
                report = self.service.build_model()
            except Exception as e:
                logger.error(f"Async model build worker failed: {e}")
                report = {"success": False, "error": str(e), "status": "INVALID"}
            
            # Queue callback safely on the main GUI thread
            try:
                widget.after(0, lambda: on_complete_callback(report))
            except Exception as e:
                logger.error(f"Failed to post complete callback on GUI thread: {e}")

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
