# ==============================================================================
# Face Recognition Attendance System - Face Recognition Service
# ==============================================================================

import os
import cv2
import json
import logging
import time
from datetime import datetime
import numpy as np
from pathlib import Path
from src.core.config import ConfigLoader
from src.core import constants
from src.core.models import FaceDataset, Student
from src.core.database import get_session
from src.repositories.student_repository import StudentRepository
from src.services.image_processing_service import ImageProcessingService

logger = logging.getLogger("app.recognition")

class FaceRecognitionService:
    """
    Dedicated Face Recognition Engine using OpenCV's LBPH Face Recognizer.
    Responsible for initializing, training, updating, loading models,
    and performing live recognition on frames/crops.
    """
    _instance = None

    @classmethod
    def get_instance(cls, settings=None):
        """
        Singleton accessor to ensure model is not loaded multiple times.
        """
        if cls._instance is None:
            cls._instance = cls(settings)
        return cls._instance

    def __init__(self, settings=None) -> None:
        self.settings = settings or ConfigLoader.load_config()
        self.student_repo = StudentRepository()
        self.image_processor = ImageProcessingService(
            target_size=(constants.FACE_ALIGN_SIZE, constants.FACE_ALIGN_SIZE)
        )
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.model_loaded = False
        self.metadata = {}
        
        # Resolve model paths
        self.model_dir = Path(self.settings.model_path)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.model_file = self.model_dir / "recognition_model.xml"
        self.metadata_file = self.model_dir / "recognition_model_metadata.json"

        # Attempt startup model loading
        self.load_model()

    def get_model_status(self) -> str:
        """
        Evaluates the current recognition model/index status.
        Returns: NOT_BUILT, READY, OUTDATED, INVALID, BUILDING
        """
        if not self.model_file.exists():
            return "NOT_BUILT"

        if not self.model_loaded or not self.metadata:
            # File exists but not loaded/metadata missing -> try loading first
            success = self.load_model()
            if not success:
                return "INVALID"

        # If loaded, check if outdated
        if self.is_model_outdated():
            return "OUTDATED"

        return "READY"

    def is_student_in_model(self, student_id: int) -> bool:
        """
        Checks if the given student is trained and included in the active loaded model.
        """
        if not self.model_loaded or not self.metadata:
            return False
        trained_ids = self.metadata.get("trained_student_ids", [])
        return student_id in trained_ids

    def is_model_outdated(self) -> bool:
        """
        Compares the loaded model metadata against database student dataset timestamps
        to identify if a rebuild is required.
        """
        if not self.model_loaded or not self.metadata:
            return True

        trained_student_ids = set(self.metadata.get("trained_student_ids", []))
        model_updated_at_str = self.metadata.get("updated_at")
        if not model_updated_at_str:
            return True
            
        try:
            model_updated_at = datetime.fromisoformat(model_updated_at_str)
        except ValueError:
            return True

        # Query all active students with READY datasets in the database
        with get_session() as session:
            ready_datasets = session.query(FaceDataset).filter(FaceDataset.status == "READY").all()
            db_student_ids = {ds.student_id for ds in ready_datasets}

            # 1. Check for ID mismatches (new ready datasets, or deleted students)
            if db_student_ids != trained_student_ids:
                return True

            # 2. Check if any dataset was updated after the model
            for ds in ready_datasets:
                ds_updated = ds.updated_at
                # If dataset updated time is newer than model training time, model is outdated
                if ds_updated > model_updated_at:
                    return True

        return False

    def load_model(self) -> bool:
        """
        Loads the LBPH model from disk and parses the companion metadata JSON.
        """
        if not self.model_file.exists() or not self.metadata_file.exists():
            self.model_loaded = False
            self.metadata = {}
            return False

        try:
            logger.info(f"Loading recognition model from: {self.model_file}")
            self.recognizer.read(str(self.model_file))
            
            logger.info(f"Reading model metadata from: {self.metadata_file}")
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)

            self.model_loaded = True
            logger.info("Recognition model loaded successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to load recognition model or metadata: {e}", exc_info=True)
            self.model_loaded = False
            self.metadata = {}
            return False

    def build_model(self) -> dict:
        """
        Compiles the recognition model from scratch using validated student datasets.
        Returns:
            report (dict): Summary of the build including count of students trained, skipped, and errors.
        """
        logger.info("Initiating recognition model building process...")
        
        report = {
            "success": False,
            "status": "NOT_BUILT",
            "students_included": 0,
            "images_included": 0,
            "students_skipped": 0,
            "skipped_details": [],
            "error": None
        }

        try:
            faces = []
            labels = []
            trained_ids = []
            trained_students_info = {}

            with get_session() as session:
                # Query all datasets. Eager load student profiles
                datasets = session.query(FaceDataset).all()

                for dataset in datasets:
                    student = dataset.student
                    # Skip inactive or deleted students, or non-READY datasets
                    if not student or student.status != "Active":
                        report["students_skipped"] += 1
                        report["skipped_details"].append(f"{student.student_code if student else 'Unknown'} - Student Inactive")
                        continue

                    if dataset.status != "READY":
                        report["students_skipped"] += 1
                        report["skipped_details"].append(f"{student.student_code} - Dataset status is {dataset.status}")
                        continue

                    # Load images in dataset
                    images = dataset.images
                    if not images or len(images) < self.settings.target_image_count:
                        report["students_skipped"] += 1
                        report["skipped_details"].append(f"{student.student_code} - Insufficient image files ({len(images)})")
                        continue

                    student_images_loaded = 0
                    for img in images:
                        img_path = Path(img.file_path)
                        if not img_path.exists():
                            continue

                        # Read image in grayscale
                        gray_img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
                        if gray_img is None:
                            continue

                        # Verify target size
                        h, w = gray_img.shape[:2]
                        if w != constants.FACE_ALIGN_SIZE or h != constants.FACE_ALIGN_SIZE:
                            # Auto-resize if somehow sizing mismatched
                            gray_img = cv2.resize(gray_img, (constants.FACE_ALIGN_SIZE, constants.FACE_ALIGN_SIZE))

                        faces.append(gray_img)
                        labels.append(student.id)
                        student_images_loaded += 1

                    if student_images_loaded > 0:
                        trained_ids.append(student.id)
                        trained_students_info[str(student.id)] = {
                            "student_code": student.student_code,
                            "name": f"{student.first_name} {student.last_name}",
                            "dataset_updated_at": dataset.updated_at.isoformat()
                        }
                        report["students_included"] += 1
                        report["images_included"] += student_images_loaded
                    else:
                        report["students_skipped"] += 1
                        report["skipped_details"].append(f"{student.student_code} - Could not read any images")

            # Check if we have data to train
            if not faces:
                err_msg = "No valid, preprocessed student datasets available for training."
                logger.warning(err_msg)
                report["error"] = err_msg
                # If training failed, delete old model to prevent stale recognition
                self.delete_model_files()
                return report

            logger.info(f"Training LBPH model with {len(faces)} images from {len(trained_ids)} students...")
            
            # Perform LBPH training
            new_recognizer = cv2.face.LBPHFaceRecognizer_create()
            new_recognizer.train(faces, np.array(labels, dtype=np.int32))
            
            # Save XML model
            new_recognizer.write(str(self.model_file))

            # Build metadata JSON
            now_iso = datetime.utcnow().isoformat()
            metadata = {
                "model_version": "1.0.0",
                "created_at": now_iso,
                "updated_at": now_iso,
                "student_count": len(trained_ids),
                "image_count": len(labels),
                "recognition_method": "LBPH",
                "configuration_version": "1.0",
                "trained_student_ids": trained_ids,
                "trained_students_info": trained_students_info
            }

            # Write metadata file
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=4)

            # Re-sync local instance state
            self.recognizer = new_recognizer
            self.metadata = metadata
            self.model_loaded = True
            
            report["success"] = True
            report["status"] = "READY"
            logger.info("Recognition model building completed successfully.")
            return report

        except Exception as e:
            logger.exception("Error building face recognition model:")
            report["error"] = str(e)
            self.delete_model_files()
            return report

    def delete_model_files(self) -> None:
        """
        Helper to wipe model files in case of build failure or resets.
        """
        try:
            if self.model_file.exists():
                os.remove(self.model_file)
            if self.metadata_file.exists():
                os.remove(self.metadata_file)
        except Exception as e:
            logger.error(f"Failed to clear model files: {e}")
        self.model_loaded = False
        self.metadata = {}

    def preprocess_face(self, bgr_frame, box: tuple[int, int, int, int]) -> np.ndarray:
        """
        Standardizes face crop: crop, resize to 112x112, and convert to grayscale.
        Guarantees deterministic inputs matching the dataset validation loop.
        """
        # Crop and resize
        crop = self.image_processor.crop_and_resize(bgr_frame, box)
        
        # Convert to grayscale
        if len(crop.shape) == 3:
            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        else:
            gray = crop
            
        return gray

    def recognize_face_crop(self, gray_face) -> tuple[int | None, float]:
        """
        Scores a preprocessed grayscale face crop against the trained model index.
        Returns:
            student_id (int or None): Matched student PK, or None if matching fails.
            similarity (float): Cosine-like similarity score mapped to [0.0, 1.0].
        """
        if not self.model_loaded:
            return None, 0.0

        try:
            # Predict returns (label, distance)
            label_id, distance = self.recognizer.predict(gray_face)
            
            # Map LBPH chi-square distance to similarity [0.0, 1.0]
            # LBPH distance normally ranges from 0 to 100+ (lower is better)
            similarity = max(0.0, min(1.0, 1.0 - (distance / 100.0)))
            
            # Validate label belongs to trained pool
            trained_student_ids = self.metadata.get("trained_student_ids", [])
            if label_id not in trained_student_ids:
                return None, similarity

            return label_id, similarity
        except Exception as e:
            logger.error(f"Error predicting face: {e}")
            return None, 0.0

    def recognize_frame(self, bgr_frame, boxes: list[tuple[int, int, int, int]], threshold: float = None) -> list[dict]:
        """
        Detects, processes, and queries matching records for multiple faces in a camera frame.
        Returns:
            results (list[dict]): Structured recognition outputs matching requirements.
        """
        if threshold is None:
            threshold = self.settings.recognition_threshold

        results = []
        if bgr_frame is None or bgr_frame.size == 0 or not boxes:
            return results

        # Query student details mapping if model is loaded
        for box in boxes:
            start_time = time.perf_counter()
            x, y, w, h = box
            
            # 1. Preprocess
            gray_face = self.preprocess_face(bgr_frame, box)
            
            # 2. Score
            student_id, similarity = self.recognize_face_crop(gray_face)
            
            processing_time = (time.perf_counter() - start_time) * 1000.0  # MS
            
            # 3. Evaluate Threshold and Map identity
            if student_id is not None and similarity >= threshold:
                student = self.student_repo.get_by_id(student_id)
                if student:
                    results.append({
                        "recognized": True,
                        "student_id": student.id,
                        "student_code": student.student_code,
                        "student_name": f"{student.first_name} {student.last_name}",
                        "roll_number": student.roll_number,
                        "distance_or_similarity": similarity,
                        "threshold": threshold,
                        "bounding_box": box,
                        "processing_time": processing_time,
                        "reason": "Match succeeded"
                    })
                    continue

            # Fallback to UNKNOWN if match is invalid or below threshold
            results.append({
                "recognized": False,
                "student_id": None,
                "student_code": "UNKNOWN",
                "student_name": "Unknown",
                "roll_number": None,
                "distance_or_similarity": similarity,
                "threshold": threshold,
                "bounding_box": box,
                "processing_time": processing_time,
                "reason": "Similarity score below threshold" if similarity < threshold else "Missing database student"
            })

        return results

    def release_resources(self) -> None:
        """
        Clears local reference allocations (conforming to interface requirements).
        """
        pass
