# ==============================================================================
# Face Recognition Attendance System - Faculty Registry Page View
# ==============================================================================

from src.gui.pages.base import BasePage

class FacultyPage(BasePage):
    """
    Faculty Management Page View. Represents Phase 4 Faculty Onboarding & Assignments.
    """
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            title="Faculty Management",
            description="Manage faculty profiles, department assignments, and class scheduling permissions.",
            phase=4
        )
