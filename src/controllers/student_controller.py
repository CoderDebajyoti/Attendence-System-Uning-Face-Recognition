# ==============================================================================
# Face Recognition Attendance System - Student Controller
# ==============================================================================

from src.services.student_service import StudentService

class StudentController:
    """
    Coordinates presentation events from StudentsPage and dialog overlays,
    delegating validations and database commits to the StudentService.
    """
    def __init__(self) -> None:
        self.service = StudentService()

    def get_filtered_students(self, **filters) -> list:
        """
        Retrieves matching student lists based on search/filter constraints.
        """
        return self.service.list_students(**filters)

    def get_departments(self) -> list:
        """
        Exposes academic departments list.
        """
        return self.service.get_departments()

    def get_courses(self, department_id: int = None) -> list:
        """
        Exposes academic courses list (optionally filtered by department).
        """
        return self.service.get_courses(department_id)

    def get_student_details(self, student_id: int):
        """
        Retrieves complete database details card.
        """
        return self.service.get_student_by_id(student_id)

    def get_dashboard_statistics(self) -> dict:
        """
        Retrieves numeric count telemetry for student registrations.
        """
        return self.service.get_statistics()

    def delete_student(self, student_id: int) -> bool:
        """
        Executes cascade student removal.
        """
        return self.service.delete_student(student_id)

    def save_student(self, student_data: dict, is_edit: bool = False, student_id: int = None) -> tuple[bool, str]:
        """
        Enforces validation rules and commits updates/new profiles.
        """
        return self.service.save_student(student_data, is_edit, student_id)
