# ==============================================================================
# Face Recognition Attendance System - Courses Page View
# ==============================================================================

from src.gui.pages.base import BasePage

class CoursesPage(BasePage):
    """
    Courses Management Page View. Represents Phase 4 Academic Setup.
    """
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            title="Course Curriculum",
            description="Configure academic programs, divisions, semestral pathways, and class capacity constraints.",
            phase=4
        )
