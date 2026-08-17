# ==============================================================================
# Face Recognition Attendance System - Reports Controller
# ==============================================================================

import logging
from src.services.attendance_report_service import AttendanceReportService
from src.services.student_service import StudentService

logger = logging.getLogger("app.system")

class ReportsController:
    """
    Coordinates presentation logic and event handlers from the ReportsPage GUI
    to the underlying AttendanceReportService and StudentService layers.
    """

    def __init__(self) -> None:
        self.report_service = AttendanceReportService.get_instance()
        self.student_service = StudentService()
        logger.info("ReportsController initialized successfully.")

    def validate_date_range(self, start_date: str, end_date: str) -> tuple[bool, str]:
        """
        Validates start and end date inputs.
        """
        return self.report_service.validate_date_range(start_date, end_date)

    def generate_report(
        self,
        start_date: str,
        end_date: str,
        status: str | None = None,
        department_id: int | None = None,
        course_id: int | None = None,
        source: str | None = None,
        student_id: int | None = None,
        search_query: str | None = None
    ) -> dict:
        """
        Gathers report rows and aggregates statistics.
        """
        return self.report_service.generate_report_data(
            start_date=start_date,
            end_date=end_date,
            status=status,
            department_id=department_id,
            course_id=course_id,
            source=source,
            student_id=student_id,
            search_query=search_query
        )

    def export_csv(self, report_data: dict) -> tuple[bool, str]:
        """
        Triggers CSV file write output.
        """
        return self.report_service.export_to_csv(report_data)

    def export_excel(self, report_data: dict) -> tuple[bool, str]:
        """
        Triggers Excel workbook write output.
        """
        return self.report_service.export_to_excel(report_data)

    def get_departments(self) -> list:
        """
        Returns all registered departments for filter lists.
        """
        return self.student_service.get_departments()

    def get_courses(self, department_id: int | None = None) -> list:
        """
        Returns all registered courses for filter lists.
        """
        return self.student_service.get_courses(department_id)

    def list_students(self) -> list:
        """
        Returns all registered students for selection filters.
        """
        return self.student_service.list_students()
