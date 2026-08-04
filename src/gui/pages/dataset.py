# ==============================================================================
# Face Recognition Attendance System - Dataset Page View
# ==============================================================================

from src.gui.pages.base import BasePage

class DatasetPage(BasePage):
    """
    Dataset Management Page View. Represents Phase 5 Face Dataset Collection & Validation.
    """
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            title="Biometric Dataset Manager",
            description="Acquire facial training samples, monitor crop quality values, and synchronize vector index records.",
            phase=5
        )
