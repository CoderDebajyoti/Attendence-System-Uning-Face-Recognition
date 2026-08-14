# ==============================================================================
# Face Recognition Attendance System - Face Dataset Controller
# ==============================================================================

from src.services import DatasetService, StudentService
import logging

logger = logging.getLogger("app.system")

class DatasetController:
    """
    Coordinates presentation logic and event handlers from the DatasetPage GUI
    to the underlying DatasetService and StudentService layers.
    """

    def __init__(self) -> None:
        self.service = DatasetService()
        self.student_service = StudentService()
        logger.info("DatasetController initialized successfully.")

    def get_active_students(self) -> list:
        """
        Retrieves all active students in the registry.
        """
        return self.student_service.list_students(status="Active")

    def get_student_details(self, student_id: int):
        """
        Retrieves profile details for a given student ID.
        """
        return self.student_service.get_student_by_id(student_id)

    def get_dataset_details(self, student_id: int):
        """
        Retrieves or initializes the FaceDataset record for the student.
        """
        try:
            return self.service.get_or_create_dataset(student_id)
        except Exception as e:
            logger.error(f"Error fetching dataset details: {e}")
            return None

    def get_target_image_count(self) -> int:
        """
        Returns the configured target count for face images.
        """
        return self.service.settings.target_image_count

    def capture_image(self, student_id: int, frame) -> tuple[bool, str, dict]:
        """
        Captures and processes a single face image crop from the camera frame.
        """
        return self.service.capture_image(student_id, frame)

    def delete_image(self, student_id: int, image_id: int) -> bool:
        """
        Deletes a single captured image from the filesystem and database.
        """
        return self.service.delete_image(student_id, image_id)

    def clear_dataset(self, student_id: int) -> bool:
        """
        Permanently deletes all captured images and clears database metadata.
        """
        return self.service.clear_dataset(student_id)

    def validate_dataset(self, student_id: int) -> dict:
        """
        Executes complete verification checklist and updates dataset status.
        """
        return self.service.validate_dataset(student_id)
