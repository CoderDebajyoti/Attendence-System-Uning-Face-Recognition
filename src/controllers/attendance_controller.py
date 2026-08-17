# ==============================================================================
# Face Recognition Attendance System - Attendance Controller
# ==============================================================================

from src.services.attendance_service import AttendanceService, AttendanceResult
from src.services.student_service import StudentService
import logging

logger = logging.getLogger("app.system")

class AttendanceController:
    """
    Coordinates presentation logic and event handlers from the Attendance Page GUI
    to the underlying AttendanceService and StudentService layers.
    """

    def __init__(self) -> None:
        self.service = AttendanceService.get_instance()
        self.student_service = StudentService()
        logger.info("AttendanceController initialized successfully.")

    def mark_attendance(self, student_id: int, score: float, method: str = "LBPH") -> AttendanceResult:
        """
        Processes biometric recognition events into attendance logs.
        """
        return self.service.mark_attendance(
            student_id=student_id,
            source="FACE_RECOGNITION",
            score=score,
            method=method
        )

    def mark_attendance_manual(
        self,
        student_id: int,
        date_str: str,
        status: str,
        reason: str,
        marked_by: str = "Admin"
    ) -> AttendanceResult:
        """
        Enforces transaction-safe manual check-in marks.
        """
        return self.service.mark_attendance(
            student_id=student_id,
            source="MANUAL",
            status=status.upper(),
            date=date_str,
            marked_by=marked_by,
            score=None,
            method=None
        )

    def update_attendance(self, record_id: int, status: str, updated_by: str = "Admin") -> tuple[bool, str]:
        """
        Modifies status of an existing attendance record.
        """
        return self.service.update_attendance(record_id, status, updated_by)

    def delete_attendance(self, record_id: int) -> bool:
        """
        Removes an attendance record.
        """
        return self.service.delete_attendance(record_id)

    def get_filtered_attendance(self, **filters) -> list:
        """
        Retrieves matching attendance records.
        """
        return self.service.list_attendance(**filters)

    def get_sessions(self) -> list:
        """
        Retrieves all tracking sessions.
        """
        return self.service.list_sessions()

    def get_today_statistics(self) -> dict:
        """
        Aggregates operational metrics for today's check-ins.
        """
        return self.service.get_today_statistics()

    def get_student_attendance_summary(self, student_id: int) -> dict:
        """
        Returns stats metrics for a student.
        """
        return self.service.get_student_attendance_summary(student_id)

    def get_student_attendance_history(self, student_id: int, limit: int = 5) -> list:
        """
        Returns recent logs for a student.
        """
        return self.service.get_recent_student_records(student_id, limit)

    def get_departments(self) -> list:
        """
        Returns registered academic departments (reusing StudentService).
        """
        return self.student_service.get_departments()

    def get_courses(self, department_id: int = None) -> list:
        """
        Returns registered academic courses (reusing StudentService).
        """
        return self.student_service.get_courses(department_id)

    def list_students(self, **filters) -> list:
        """
        Lists all students (useful for manual selection dropdowns).
        """
        return self.student_service.list_students(**filters)
