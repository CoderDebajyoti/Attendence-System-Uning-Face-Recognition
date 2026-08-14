# ==============================================================================
# Face Recognition Attendance System - Face Dataset Service
# ==============================================================================

import os
import shutil
import cv2
import logging
from datetime import datetime
from pathlib import Path
from src.core.config import ConfigLoader
from src.core import constants
from src.core.models import FaceDataset, DatasetImage
from src.repositories import DatasetRepository, StudentRepository
from src.services.face_detector_service import FaceDetectorService
from src.services.image_processing_service import ImageProcessingService

logger = logging.getLogger("app.recognition")

class DatasetService:
    """
    Orchestrates face dataset capture, deletion, directory clear, and validation.
    Integrates database records, file operations, and computer vision validation.
    """

    def __init__(self, settings=None) -> None:
        self.settings = settings or ConfigLoader.load_config()
        self.repo = DatasetRepository()
        self.student_repo = StudentRepository()
        self.face_detector = FaceDetectorService()
        self.image_processor = ImageProcessingService(
            target_size=(constants.FACE_ALIGN_SIZE, constants.FACE_ALIGN_SIZE)
        )
        logger.info("DatasetService initialized successfully.")

    def get_or_create_dataset(self, student_id: int) -> FaceDataset:
        """
        Retrieves or creates a FaceDataset record for the student.
        """
        dataset = self.repo.get_by_student_id(student_id)
        if not dataset:
            student = self.student_repo.get_by_id(student_id)
            if not student:
                raise ValueError(f"Student with database ID {student_id} not found.")

            # Resolve student-specific crop directory: database/datasets/students/<student_code>
            student_dir = Path(self.settings.dataset_path) / "students" / student.student_code
            dataset = self.repo.create_dataset(student_id, str(student_dir))
        return dataset

    def capture_image(self, student_id: int, frame) -> tuple[bool, str, dict]:
        """
        Processes a single camera frame:
        - Runs single face detection checks.
        - Crops and resizes face to 112x112.
        - Evaluates image quality (blurriness, brightness).
        - Saves the file safely under the student's dataset directory.
        - Commits a new DatasetImage record.
        - Updates the dataset image count.
        """
        try:
            # 1. Face count and boundary validation
            is_valid, msg, boxes = self.face_detector.validate_face_for_dataset(frame)
            if not is_valid:
                return False, msg, {}

            box = boxes[0]

            # 2. Crop and resize crop
            crop = self.image_processor.crop_and_resize(frame, box)

            # 3. Quality assurance checks
            is_good, q_msg = self.image_processor.check_quality(crop)
            if not is_good:
                return False, q_msg, {}

            # 4. Fetch or instantiate dataset model
            dataset = self.get_or_create_dataset(student_id)
            dest_dir = Path(dataset.dataset_path)
            dest_dir.mkdir(parents=True, exist_ok=True)

            # 5. Determine the next sequence index for safe filename image_xxx.jpg
            existing_imgs = dataset.images
            existing_indices = []
            for img in existing_imgs:
                filename = Path(img.file_path).name
                if filename.startswith("image_") and filename.endswith(".jpg"):
                    try:
                        num = int(filename[6:-4])
                        existing_indices.append(num)
                    except ValueError:
                        pass

            next_idx = 1
            if existing_indices:
                next_idx = max(existing_indices) + 1

            filename = f"image_{next_idx:03d}.jpg"
            file_path = dest_dir / filename

            # 6. Save image crop to filesystem
            if not self.image_processor.save_image(crop, str(file_path)):
                return False, "Failed to save the image crop on disk.", {}

            # 7. Insert DB record
            db_img = self.repo.add_image(student_id, str(file_path))

            # 8. Update dataset image count and status
            new_count = len(existing_imgs) + 1
            current_status = dataset.status
            if current_status == "NOT_REGISTERED" or current_status == "INVALID":
                current_status = "COLLECTING"

            self.repo.update_dataset(student_id, new_count, current_status)

            return True, "Face detected. Image captured.", {
                "id": db_img.id,
                "file_path": db_img.file_path,
                "filename": filename
            }

        except Exception as e:
            logger.error(f"Error during capture_image service execution: {e}", exc_info=True)
            return False, f"System error: {str(e)}", {}

    def delete_image(self, student_id: int, image_id: int) -> bool:
        """
        Removes a single image from the database and disk.
        """
        db_img = self.repo.get_image_by_id(image_id)
        if not db_img:
            return False

        # Remove image crop file
        file_path = Path(db_img.file_path)
        if file_path.exists():
            try:
                os.remove(file_path)
            except Exception as e:
                logger.error(f"Failed to delete file {file_path}: {e}")

        # Delete database row
        success = self.repo.delete_image(student_id, image_id)
        if success:
            dataset = self.repo.get_by_student_id(student_id)
            if dataset:
                new_count = len(dataset.images)
                new_status = dataset.status
                if new_count == 0:
                    new_status = "NOT_REGISTERED"
                elif new_count < self.settings.target_image_count and new_status == "READY":
                    new_status = "NEEDS_UPDATE"

                self.repo.update_dataset(student_id, new_count, new_status)
        return success

    def clear_dataset(self, student_id: int) -> bool:
        """
        Clears the entire dataset for a student, deleting the folder and DB rows.
        """
        dataset = self.repo.get_by_student_id(student_id)
        if not dataset:
            # Verify if student exists before attempting database clear
            student = self.student_repo.get_by_id(student_id)
            if not student:
                return False
            # If student exists but dataset does not, just reset status
            with get_session() as session:
                from src.core.models import Student
                s = session.query(Student).filter(Student.id == student_id).first()
                if s:
                    s.face_dataset_status = "NOT_REGISTERED"
                    session.commit()
            return True

        dir_path = Path(dataset.dataset_path)
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path)
            except Exception as e:
                logger.error(f"Failed to clear directory {dir_path}: {e}")

        return self.repo.clear_dataset(student_id)

    def validate_dataset(self, student_id: int) -> dict:
        """
        Conducts a rigorous validation check on all saved crops in the student's dataset.
        Checks:
        - Image count vs target_image_count.
        - Physical file existence.
        - Image readability.
        - Face alignment size (112x112).
        - Singular face detection inside the crop.
        Returns a structured validation result and updates database status.
        """
        dataset = self.get_or_create_dataset(student_id)
        images = dataset.images
        target_count = self.settings.target_image_count

        errors = []
        successes = []

        dir_path = Path(dataset.dataset_path)
        if not dir_path.exists():
            errors.append("Dataset directory does not exist on disk.")
        else:
            successes.append("Dataset directory exists.")

        count = len(images)
        if count < target_count:
            errors.append(f"Insufficient images: found {count}, required {target_count}.")
        else:
            successes.append(f"{count} images found (Target: {target_count}).")

        readable_count = 0
        dimension_count = 0
        face_count = 0

        # Create secondary smaller face detector for crop validation checks
        crop_face_detector = FaceDetectorService(min_face_size=40)

        for img in images:
            p = Path(img.file_path)
            if not p.exists():
                errors.append(f"File missing on disk: {p.name}")
                continue

            frame = cv2.imread(str(p))
            if frame is None:
                errors.append(f"Corrupted or unreadable image: {p.name}")
                continue

            readable_count += 1

            h, w = frame.shape[:2]
            if w != constants.FACE_ALIGN_SIZE or h != constants.FACE_ALIGN_SIZE:
                errors.append(f"Invalid dimensions for {p.name}: {w}x{h} (expected {constants.FACE_ALIGN_SIZE}x{constants.FACE_ALIGN_SIZE})")
            else:
                dimension_count += 1

            boxes = crop_face_detector.detect_faces(frame)
            if len(boxes) != 1:
                errors.append(f"Image {p.name} does not contain exactly one face (found {len(boxes)}).")
            else:
                face_count += 1

        if count > 0:
            if readable_count == count:
                successes.append(f"{readable_count} / {count} readable images.")
            else:
                errors.append(f"Only {readable_count} / {count} readable images.")

            if dimension_count == count:
                successes.append(f"{dimension_count} / {count} images have valid dimensions ({constants.FACE_ALIGN_SIZE}x{constants.FACE_ALIGN_SIZE}).")

            if face_count == count:
                successes.append(f"{face_count} / {count} images contain exactly one face.")

        # Resolve status
        if errors or count < target_count:
            if count == 0:
                status = "NOT_REGISTERED"
            elif count < target_count:
                status = "NEEDS_UPDATE"
            else:
                status = "INVALID"
        else:
            status = "READY"

        validation_result_str = "; ".join(errors) if errors else "All checks passed successfully."
        now = datetime.utcnow()

        self.repo.update_dataset(
            student_id=student_id,
            image_count=count,
            status=status,
            last_validation=now,
            validation_result=validation_result_str
        )

        return {
            "success": len(errors) == 0 and count >= target_count,
            "status": status,
            "errors": errors,
            "successes": successes,
            "validation_result": validation_result_str,
            "last_validation": now.strftime("%Y-%m-%d %H:%M:%S")
        }
