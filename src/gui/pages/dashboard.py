# ==============================================================================
# Face Recognition Attendance System - Dashboard Page View
# ==============================================================================

import customtkinter as ctk
from src.gui.themes import ThemeManager
from src.gui.pages.base import BasePage
from src.gui.components import Card, StatisticWidget

class DashboardPage(BasePage):
    """
    Dashboard Page View. Displays core KPI metrics cards, system statuses,
    and active console log outputs.
    """
    def __init__(self, parent, controller) -> None:
        super().__init__(
            parent=parent,
            controller=controller,
            title="System Dashboard",
            description="Operational metrics overview and biometric engine status diagnostics.",
            phase=7
        )
        
    def show_default_placeholder(self) -> None:
        """
        Overrides base class to build a professional dashboard metrics panel.
        """
        # Fetch real-time statistics from DB
        from src.controllers import StudentController
        from src.controllers.attendance_controller import AttendanceController
        self.student_controller = StudentController()
        self.attendance_controller = AttendanceController()
        
        try:
            stats = self.student_controller.get_dashboard_statistics()
        except Exception:
            stats = {
                "total": 0,
                "active": 0,
                "inactive": 0,
                "with_dataset": 0,
                "without_dataset": 0
            }

        try:
            att_stats = self.attendance_controller.get_today_statistics()
        except Exception:
            att_stats = {
                "total_marked": 0,
                "present": 0,
                "late": 0,
                "rate": 0.0,
                "total_students": 0
            }

        # Configure layout grids
        self.content_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.content_frame.grid_rowconfigure((1, 2), weight=1)
        
        # 1. Row 0: KPI Summary Statistics Widgets
        self.student_stat = StatisticWidget(
            self.content_frame, 
            title="Total Enrolled Students", 
            value=f"{stats['total']} Students", 
            accent_color=ThemeManager.get_color("accent_secondary"),
            icon="👥"
        )
        self.student_stat.grid(row=0, column=0, sticky="nsew", padx=ThemeManager.PAD_SM, pady=ThemeManager.PAD_SM)
        
        self.dataset_stat = StatisticWidget(
            self.content_frame, 
            title="Trained Biometric Profiles", 
            value=f"{stats['with_dataset']} Profiles",
            accent_color=ThemeManager.get_color("accent_primary"),
            icon="📂"
        )
        self.dataset_stat.grid(row=0, column=1, sticky="nsew", padx=ThemeManager.PAD_SM, pady=ThemeManager.PAD_SM)
        
        self.attendance_stat = StatisticWidget(
            self.content_frame, 
            title="Today's Attendance", 
            value=f"{att_stats['present'] + att_stats['late']} / {att_stats['total_students']} Present ({att_stats['rate']}%)", 
            accent_color=ThemeManager.get_color("accent_success"),
            icon="📝"
        )
        self.attendance_stat.grid(row=0, column=2, sticky="nsew", padx=ThemeManager.PAD_SM, pady=ThemeManager.PAD_SM)
        
        # 2. Row 1: Configurations and Biometric Diagnostic Panels
        self.create_system_status_panel(row=1, col=0, columnspan=2)
        self.create_biometric_diagnostics_panel(row=1, col=2, stats=stats)
        
        # 3. Row 2: Console Log Tracer Panel
        self.create_activity_panel(row=2, col=0, columnspan=3)

    def create_system_status_panel(self, row: int, col: int, columnspan: int) -> None:
        """
        Builds a status card representing loaded configuration variables.
        """
        panel = Card(self.content_frame)
        panel.grid(row=row, column=col, columnspan=columnspan, sticky="nsew", padx=ThemeManager.PAD_SM, pady=ThemeManager.PAD_SM)
        panel.grid_columnconfigure(1, weight=1)
        
        title = ctk.CTkLabel(
            panel, 
            text="System Core Settings", 
            font=ThemeManager.get_font(size=14, weight="bold"),
            text_color=ThemeManager.get_color("text_primary")
        )
        title.grid(row=0, column=0, columnspan=2, sticky="w", padx=ThemeManager.PAD_LG, pady=ThemeManager.PAD_LG)
        
        # Mapping config data rows
        settings_info = [
            ("Environment Mode", "development", ThemeManager.get_color("accent_primary")),
            ("Database Location", "sqlite:///database/app_database.db", ThemeManager.get_color("text_light")),
            ("Log Level Priority", "INFO", ThemeManager.get_color("text_muted")),
            ("Model Directory Path", "models/", ThemeManager.get_color("text_muted"))
        ]
        
        for idx, (label_txt, val_txt, val_color) in enumerate(settings_info):
            lbl = ctk.CTkLabel(panel, text=label_txt, font=ThemeManager.get_font(size=12), text_color=ThemeManager.get_color("text_light"))
            lbl.grid(row=idx+1, column=0, sticky="w", padx=ThemeManager.PAD_LG, pady=ThemeManager.PAD_XS)
            
            val = ctk.CTkLabel(panel, text=val_txt, font=ThemeManager.get_font(size=12, weight="bold"), text_color=val_color)
            val.grid(row=idx+1, column=1, sticky="w", padx=ThemeManager.PAD_LG, pady=ThemeManager.PAD_XS)

    def create_biometric_diagnostics_panel(self, row: int, col: int, stats: dict) -> None:
        """
        Builds a diagnostic panel showing status of biometric engines.
        """
        panel = Card(self.content_frame)
        panel.grid(row=row, column=col, sticky="nsew", padx=ThemeManager.PAD_SM, pady=ThemeManager.PAD_SM)
        panel.grid_columnconfigure(1, weight=1)
        
        title = ctk.CTkLabel(
            panel, 
            text="Biometric Core Diagnostics", 
            font=ThemeManager.get_font(size=14, weight="bold"),
            text_color=ThemeManager.get_color("text_primary")
        )
        title.grid(row=0, column=0, columnspan=2, sticky="w", padx=ThemeManager.PAD_LG, pady=ThemeManager.PAD_LG)
        
        # Load live recognition service status
        try:
            from src.services.face_recognition_service import FaceRecognitionService
            rec_service = FaceRecognitionService.get_instance(self.controller.settings)
            model_status = rec_service.get_model_status()
            
            status_colors = {
                "READY": ThemeManager.get_color("accent_success"),
                "OUTDATED": ThemeManager.get_color("accent_warning"),
                "BUILDING": ThemeManager.get_color("accent_warning"),
                "INVALID": ThemeManager.get_color("accent_danger"),
                "NOT_BUILT": ThemeManager.get_color("text_muted")
            }
            rec_engine_text = f"Model {model_status.replace('_', ' ')}"
            rec_engine_color = status_colors.get(model_status, ThemeManager.get_color("text_primary"))
        except Exception:
            rec_engine_text = "Offline"
            rec_engine_color = ThemeManager.get_color("accent_danger")

        # Threshold value
        threshold_val = f"{self.controller.settings.recognition_threshold} (LBPH)"
        
        # Camera link
        if self.controller.settings.camera_rtsp_url:
            cam_text = "RTSP Stream Feed"
        else:
            cam_text = f"Local Device ({self.controller.settings.camera_id})"

        diagnostics = [
            ("Recognition Engine", rec_engine_text, rec_engine_color),
            ("Face Dataset Storage", f"Ready ({stats['with_dataset']} Templates)", ThemeManager.get_color("accent_success")),
            ("Confidence Threshold", threshold_val, ThemeManager.get_color("accent_secondary")),
            ("Camera Stream Link", cam_text, ThemeManager.get_color("text_light"))
        ]
        
        for idx, (label_txt, val_txt, val_color) in enumerate(diagnostics):
            lbl = ctk.CTkLabel(panel, text=label_txt, font=ThemeManager.get_font(size=12), text_color=ThemeManager.get_color("text_light"))
            lbl.grid(row=idx+1, column=0, sticky="w", padx=ThemeManager.PAD_LG, pady=ThemeManager.PAD_XS)
            
            val = ctk.CTkLabel(panel, text=val_txt, font=ThemeManager.get_font(size=12, weight="bold"), text_color=val_color)
            val.grid(row=idx+1, column=1, sticky="w", padx=ThemeManager.PAD_LG, pady=ThemeManager.PAD_XS)

    def create_activity_panel(self, row: int, col: int, columnspan: int) -> None:
        """
        Displays system events activity logs inside a styled card.
        """
        panel = Card(self.content_frame)
        panel.grid(row=row, column=col, columnspan=columnspan, sticky="nsew", padx=ThemeManager.PAD_SM, pady=ThemeManager.PAD_SM)
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)
        
        title = ctk.CTkLabel(
            panel, 
            text="Recent Activity Log Diagnostics", 
            font=ThemeManager.get_font(size=14, weight="bold"),
            text_color=ThemeManager.get_color("text_primary")
        )
        title.grid(row=0, column=0, sticky="w", padx=ThemeManager.PAD_LG, pady=(ThemeManager.PAD_LG, ThemeManager.PAD_SM))
        
        log_box = ctk.CTkTextbox(
            panel, 
            font=("Consolas", 11),
            fg_color=ThemeManager.get_color("bg_main"), 
            text_color=ThemeManager.get_color("text_light"),
            border_color=ThemeManager.get_color("border"),
            border_width=ThemeManager.BORDER_WIDTH,
            corner_radius=ThemeManager.CORNER_RADIUS_SM
        )
        log_box.grid(row=1, column=0, sticky="nsew", padx=ThemeManager.PAD_LG, pady=(0, ThemeManager.PAD_LG))
        
        # Populate logs from active logs file
        from pathlib import Path
        log_path = Path("logs/app_system.log")
        log_content = ""
        if log_path.exists():
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    log_content = "".join(lines[-35:])
            except Exception as e:
                log_content = f"Error reading active diagnostics logs: {e}"
        else:
            log_content = "System log file 'logs/app_system.log' not found."

        log_box.insert("0.0", log_content)
        log_box.configure(state="disabled") # Read only
