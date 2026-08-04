# ==============================================================================
# Face Recognition Attendance System - Subjects Page View
# ==============================================================================

from src.gui.pages.base import BasePage

class SubjectsPage(BasePage):
    """
    Subjects Management Page View. Represents Phase 4 Subject Layout.
    """
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            title="Subject Catalog",
            description="Manage specific course topics, syllabus units, and faculty-to-subject associations.",
            phase=4
        )
