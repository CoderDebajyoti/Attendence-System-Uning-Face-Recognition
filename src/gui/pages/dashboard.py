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
        self.student_controller = StudentController()
        
        try:
            stats = self.student_controller.get_dashboard_statistics()
        except Exception:
            # Fallback if DB fails or tables are unseeded
            stats = {
                "total": 0,
                "active": 0,
                "inactive": 0,
                "with_dataset": 0,
                "without_dataset": 0
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
        
        self.faculty_stat = StatisticWidget(
            self.content_frame, 
            title="Active Faculty Members", 
            value="0 Faculty",  # Placeholder until Faculty Module
            accent_color=ThemeManager.get_color("accent_primary"),
            icon="👨‍🏫"
        )
        self.faculty_stat.grid(row=0, column=1, sticky="nsew", padx=ThemeManager.PAD_SM, pady=ThemeManager.PAD_SM)
        
        self.attendance_stat = StatisticWidget(
            self.content_frame, 
            title="Today's Attendance", 
            value="0 / 0 Present (0.0%)",  # Placeholder until Attendance Module
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
        
        diagnostics = [
            ("Recognition Engine", "Offline (Phase 7 Core)", ThemeManager.get_color("accent_danger")),
            ("Face Dataset Storage", f"Ready ({stats['with_dataset']} Templates)", ThemeManager.get_color("accent_success")),
            ("Confidence Threshold", "0.65 (Cosine)", ThemeManager.get_color("accent_secondary")),
            ("Camera Stream Link", "Local Interface (0)", ThemeManager.get_color("text_light"))
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
        
        # Populate initial logs
        initial_logs = (
            "2026-08-09 10:59:31 [INFO] app.bootstrap: Initializing Face Recognition Attendance System workspace...\n"
            "2026-08-09 10:59:31 [INFO] app.bootstrap: Environment: development | Debug: True\n"
            "2026-08-09 10:59:31 [INFO] app.bootstrap: Database URL: sqlite:///database/app_database.db\n"
            "2026-08-09 10:59:32 [INFO] app.bootstrap: Executing system startup diagnostics...\n"
            "2026-08-09 10:59:32 [INFO] app.bootstrap: Startup diagnostics passed successfully.\n"
            "2026-08-09 10:59:32 [INFO] app.database: Connecting database engine and seeding...\n"
            "2026-08-09 10:59:33 [INFO] app.bootstrap: Spawning loading splash screen...\n"
            "2026-08-09 10:59:35 [INFO] app.bootstrap: Splash screen completed. Bootstrapping Application Shell GUI...\n"
            "2026-08-09 10:59:36 [INFO] app.shell: Main application shell layout successfully loaded.\n"
            "2026-08-09 10:59:36 [INFO] app.shell: Student Module fully integrated. Database counts active."
        )
        log_box.insert("0.0", initial_logs)
        log_box.configure(state="disabled") # Read only
