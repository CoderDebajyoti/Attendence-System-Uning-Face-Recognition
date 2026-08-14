# ==============================================================================
# Face Recognition Attendance System - Face Dataset Repository
# ==============================================================================

from src.core.database import get_session
from src.core.models import FaceDataset, DatasetImage, Student
from sqlalchemy.orm import joinedload
from datetime import datetime

class DatasetRepository:
    """
    Handles standard data operations for FaceDataset and DatasetImage records.
    Ensures all database models are completely expunged from sessions on exit
    to prevent lazy loading errors in other layers.
    """

    def get_by_student_id(self, student_id: int) -> FaceDataset:
        """
        Retrieves the FaceDataset record for a student, eager loading images.
        """
        with get_session() as session:
            dataset = session.query(FaceDataset).filter(FaceDataset.student_id == student_id).first()
            if dataset:
                # Force load relationships into memory
                _ = dataset.images
                # Expunge all objects loaded in this session
                session.expunge_all()
            return dataset

    def create_dataset(self, student_id: int, dataset_path: str) -> FaceDataset:
        """
        Creates a new FaceDataset record in the database.
        """
        with get_session() as session:
            dataset = FaceDataset(
                student_id=student_id,
                dataset_path=dataset_path,
                image_count=0,
                status="NOT_REGISTERED"
            )
            session.add(dataset)
            session.commit()
            session.refresh(dataset)
            _ = dataset.images
            session.expunge_all()
            return dataset

    def update_dataset(self, student_id: int, image_count: int, status: str, last_validation=None, validation_result: str = None) -> FaceDataset:
        """
        Updates metadata fields on the student's FaceDataset and syncs status back to Student.
        """
        with get_session() as session:
            dataset = session.query(FaceDataset).filter(FaceDataset.student_id == student_id).first()
            if not dataset:
                raise ValueError(f"Dataset for student {student_id} not found.")

            dataset.image_count = image_count
            dataset.status = status
            dataset.updated_at = datetime.utcnow()
            if last_validation is not None:
                dataset.last_validation = last_validation
            if validation_result is not None:
                dataset.validation_result = validation_result

            # Sync to student table
            student = session.query(Student).filter(Student.id == student_id).first()
            if student:
                student.face_dataset_status = status

            session.commit()
            session.refresh(dataset)
            _ = dataset.images
            session.expunge_all()
            return dataset

    def add_image(self, student_id: int, file_path: str) -> DatasetImage:
        """
        Registers a new image crop file path under the student's dataset.
        """
        with get_session() as session:
            dataset = session.query(FaceDataset).filter(FaceDataset.student_id == student_id).first()
            if not dataset:
                raise ValueError(f"Dataset for student {student_id} not found.")

            img = DatasetImage(
                dataset_id=dataset.id,
                file_path=file_path
            )
            session.add(img)
            session.commit()
            session.refresh(img)
            session.expunge_all()
            return img

    def get_image_by_id(self, image_id: int) -> DatasetImage:
        """
        Retrieves a DatasetImage record by its ID.
        """
        with get_session() as session:
            img = session.query(DatasetImage).filter(DatasetImage.id == image_id).first()
            if img:
                session.expunge_all()
            return img

    def delete_image(self, student_id: int, image_id: int) -> bool:
        """
        Removes a DatasetImage record from the database.
        """
        with get_session() as session:
            dataset = session.query(FaceDataset).filter(FaceDataset.student_id == student_id).first()
            if not dataset:
                return False

            img = session.query(DatasetImage).filter(
                DatasetImage.id == image_id,
                DatasetImage.dataset_id == dataset.id
            ).first()

            if not img:
                return False

            session.delete(img)
            session.commit()
            return True

    def clear_dataset(self, student_id: int) -> bool:
        """
        Deletes all image records associated with a student's dataset.
        """
        with get_session() as session:
            dataset = session.query(FaceDataset).filter(FaceDataset.student_id == student_id).first()
            if not dataset:
                return False

            session.query(DatasetImage).filter(DatasetImage.dataset_id == dataset.id).delete()
            dataset.image_count = 0
            dataset.status = "NOT_REGISTERED"
            dataset.updated_at = datetime.utcnow()
            dataset.last_validation = None
            dataset.validation_result = None

            # Sync to student
            student = session.query(Student).filter(Student.id == student_id).first()
            if student:
                student.face_dataset_status = "NOT_REGISTERED"

            session.commit()
            return True
