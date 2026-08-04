# ==============================================================================
# Face Recognition Attendance System - Departments Page View
# ==============================================================================

from src.gui.pages.base import BasePage

class DepartmentsPage(BasePage):
    """
    Departments Management Page View. Represents Phase 4 Institutional Setup.
    """
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            title="Department Directory",
            description="Structure institutional departments, abbreviations, and head designations.",
            phase=4
        )
