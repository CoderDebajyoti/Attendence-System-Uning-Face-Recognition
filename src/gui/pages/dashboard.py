# ==============================================================================
# Face Recognition Attendance System - Dashboard Page View
# ==============================================================================

import customtkinter as ctk
from src.gui.theme import Theme
from src.gui.pages.base import BasePage

class DashboardPage(BasePage):
    """
    Dashboard Page View. Displays core metrics cards, system statuses,
    and recent logging activity placeholders.
    """
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            title="System Dashboard",
            description="Operational metrics overview and biometric engine status diagnostics.",
            phase=5
        )
        
    def show_default_placeholder(self) -> None:
        """
        Overrides base class to build a dashboard layout.
        """
        # Configure content frame weights
        self.content_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.content_frame.grid_rowconfigure((1, 2), weight=1)
        
        # 1. Row 0: Summary Cards (Total Students, Faculty, Today's Attendance)
        self.create_metric_card(
            row=0, col=0, 
            title="Total Enrolled Students", 
            value="0 Students", 
            accent_color=Theme.ACCENT_SECONDARY,
            icon="👥"
        )
        self.create_metric_card(
            row=0, col=1, 
            title="Active Faculty Members", 
            value="0 Faculty", 
            accent_color=Theme.ACCENT_PRIMARY,
            icon="👨‍🏫"
        )
        self.create_metric_card(
            row=0, col=2, 
            title="Today's Attendance", 
            value="0 / 0 Present (0.0%)", 
            accent_color=Theme.ACCENT_SUCCESS,
            icon="📝"
        )
        
        # 2. Row 1: System Status Details (Left 2 Columns) & Biometric Status (Right Column)
        self.create_system_status_panel(row=1, col=0, columnspan=2)
        self.create_biometric_diagnostics_panel(row=1, col=2)
        
        # 3. Row 2: Recent System Event Logs
        self.create_activity_panel(row=2, col=0, columnspan=3)

    def create_metric_card(self, row: int, col: int, title: str, value: str, accent_color: str, icon: str) -> None:
        """
        Helper to construct a responsive, styled KPI metric card.
        """
        card = ctk.CTkFrame(
            self.content_frame, 
            fg_color=Theme.BG_CARD,
            border_color=Theme.BORDER_COLOR,
            border_width=Theme.BORDER_WIDTH,
            corner_radius=Theme.CORNER_RADIUS_MD
        )
        card.grid(row=row, column=col, sticky="nsew", padx=Theme.PAD_SM, pady=Theme.PAD_SM)
        card.grid_columnconfigure(0, weight=1)
        
        # Icon tag
        icon_label = ctk.CTkLabel(card, text=icon, font=Theme.get_font(size=24))
        icon_label.grid(row=0, column=0, sticky="w", padx=Theme.PAD_LG, pady=(Theme.PAD_LG, 0))
        
        # Value
        val_label = ctk.CTkLabel(
            card, 
            text=value, 
            font=Theme.get_font(size=22, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        val_label.grid(row=1, column=0, sticky="w", padx=Theme.PAD_LG, pady=(Theme.PAD_XS, 0))
        
        # Title
        title_label = ctk.CTkLabel(
            card, 
            text=title, 
            font=Theme.get_font(size=12),
            text_color=Theme.TEXT_MUTED
        )
        title_label.grid(row=2, column=0, sticky="w", padx=Theme.PAD_LG, pady=(0, Theme.PAD_LG))
        
        # Highlight Accent Bar at top
        accent_bar = ctk.CTkFrame(card, height=4, fg_color=accent_color)
        accent_bar.place(relx=0, rely=0, relwidth=1)

    def create_system_status_panel(self, row: int, col: int, columnspan: int) -> None:
        """
        Panel showing core settings parameters from configurations.
        """
        panel = ctk.CTkFrame(
            self.content_frame, 
            fg_color=Theme.BG_CARD,
            border_color=Theme.BORDER_COLOR,
            border_width=Theme.BORDER_WIDTH,
            corner_radius=Theme.CORNER_RADIUS_MD
        )
        panel.grid(row=row, column=col, columnspan=columnspan, sticky="nsew", padx=Theme.PAD_SM, pady=Theme.PAD_SM)
        panel.grid_columnconfigure(1, weight=1)
        
        title = ctk.CTkLabel(
            panel, 
            text="System Core Settings", 
            font=Theme.get_font(size=14, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        title.grid(row=0, column=0, columnspan=2, sticky="w", padx=Theme.PAD_LG, pady=Theme.PAD_LG)
        
        # Setting rows
        settings_info = [
            ("Environment Mode", "development", Theme.ACCENT_PRIMARY),
            ("Database Location", "sqlite:///database/app_database.db", Theme.TEXT_LIGHT),
            ("Log Level Priority", "INFO", Theme.TEXT_MUTED),
            ("Model Directory Path", "models/", Theme.TEXT_MUTED)
        ]
        
        for idx, (label_txt, val_txt, val_color) in enumerate(settings_info):
            lbl = ctk.CTkLabel(panel, text=label_txt, font=Theme.get_font(size=12), text_color=Theme.TEXT_LIGHT)
            lbl.grid(row=idx+1, column=0, sticky="w", padx=Theme.PAD_LG, pady=Theme.PAD_XS)
            
            val = ctk.CTkLabel(panel, text=val_txt, font=Theme.get_font(size=12, weight="bold"), text_color=val_color)
            val.grid(row=idx+1, column=1, sticky="w", padx=Theme.PAD_LG, pady=Theme.PAD_XS)

    def create_biometric_diagnostics_panel(self, row: int, col: int) -> None:
        """
        Panel showing biometric engines readiness indicators.
        """
        panel = ctk.CTkFrame(
            self.content_frame, 
            fg_color=Theme.BG_CARD,
            border_color=Theme.BORDER_COLOR,
            border_width=Theme.BORDER_WIDTH,
            corner_radius=Theme.CORNER_RADIUS_MD
        )
        panel.grid(row=row, column=col, sticky="nsew", padx=Theme.PAD_SM, pady=Theme.PAD_SM)
        panel.grid_columnconfigure(1, weight=1)
        
        title = ctk.CTkLabel(
            panel, 
            text="Biometric Core Diagnostics", 
            font=Theme.get_font(size=14, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        title.grid(row=0, column=0, columnspan=2, sticky="w", padx=Theme.PAD_LG, pady=Theme.PAD_LG)
        
        diagnostics = [
            ("Recognition Engine", "Disconnected", Theme.ACCENT_DANGER),
            ("Face Dataset Storage", "Not Created", Theme.ACCENT_WARNING),
            ("Confidence Threshold", "0.65 (Default)", Theme.ACCENT_SECONDARY),
            ("Camera Stream Link", "Local Interface (0)", Theme.TEXT_LIGHT)
        ]
        
        for idx, (label_txt, val_txt, val_color) in enumerate(diagnostics):
            lbl = ctk.CTkLabel(panel, text=label_txt, font=Theme.get_font(size=12), text_color=Theme.TEXT_LIGHT)
            lbl.grid(row=idx+1, column=0, sticky="w", padx=Theme.PAD_LG, pady=Theme.PAD_XS)
            
            val = ctk.CTkLabel(panel, text=val_txt, font=Theme.get_font(size=12, weight="bold"), text_color=val_color)
            val.grid(row=idx+1, column=1, sticky="w", padx=Theme.PAD_LG, pady=Theme.PAD_XS)

    def create_activity_panel(self, row: int, col: int, columnspan: int) -> None:
        """
        Displays rolling console-like system events activity logs.
        """
        panel = ctk.CTkFrame(
            self.content_frame, 
            fg_color=Theme.BG_CARD,
            border_color=Theme.BORDER_COLOR,
            border_width=Theme.BORDER_WIDTH,
            corner_radius=Theme.CORNER_RADIUS_MD
        )
        panel.grid(row=row, column=col, columnspan=columnspan, sticky="nsew", padx=Theme.PAD_SM, pady=Theme.PAD_SM)
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)
        
        title = ctk.CTkLabel(
            panel, 
            text="Recent Activity Log Diagnostics", 
            font=Theme.get_font(size=14, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        title.grid(row=0, column=0, sticky="w", padx=Theme.PAD_LG, pady=(Theme.PAD_LG, Theme.PAD_SM))
        
        # Log box content (simulated read logs)
        log_box = ctk.CTkTextbox(
            panel, 
            font=("Consolas", 11),
            fg_color=Theme.BG_MAIN, 
            text_color=Theme.TEXT_LIGHT,
            border_color=Theme.BORDER_COLOR,
            border_width=Theme.BORDER_WIDTH,
            corner_radius=Theme.CORNER_RADIUS_SM
        )
        log_box.grid(row=1, column=0, sticky="nsew", padx=Theme.PAD_LG, pady=(0, Theme.PAD_LG))
        
        # Populate initial logs
        initial_logs = (
            "2026-08-02 21:50:39 [INFO] app.bootstrap: Initializing Face Recognition Attendance System workspace...\n"
            "2026-08-02 21:50:39 [INFO] app.bootstrap: Environment: development | Debug: True\n"
            "2026-08-02 21:50:39 [INFO] app.bootstrap: Database URL: sqlite:///database/app_database.db\n"
            "2026-08-02 21:50:40 [INFO] app.bootstrap: Startup validation GUI window ready. Launching loop...\n"
            "2026-08-02 21:50:42 [INFO] app.bootstrap: Initialized directories models/, database/backups, database/exports...\n"
            "2026-08-02 21:53:23 [INFO] app.bootstrap: Active local virtual environment site-packages injected successfully.\n"
            "2026-08-02 23:07:18 [INFO] app.shell: Main application shell layout successfully loaded.\n"
            "2026-08-02 23:07:18 [INFO] app.shell: Loading navigation menus & pages..."
        )
        log_box.insert("0.0", initial_logs)
        log_box.configure(state="disabled") # Read only
