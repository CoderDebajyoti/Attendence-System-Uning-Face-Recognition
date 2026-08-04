# ==============================================================================
# Face Recognition Attendance System - Students Registry Page View
# ==============================================================================

from src.gui.pages.base import BasePage

class StudentsPage(BasePage):
    """
    Students Management Page View. Represents Phase 4 Student Onboarding & Registry.
    """
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            title="Student Management",
            description="Register student profiles, maintain enrolment statuses, and link biometric datasets.",
            phase=4
        )
