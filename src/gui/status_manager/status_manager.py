# ==============================================================================
# Face Recognition Attendance System - Status Bar Manager
# ==============================================================================

import customtkinter as ctk
from datetime import datetime
from src.gui.themes import ThemeManager

class StatusManager:
    """
    Coordinates information layout inside the bottom diagnostic ribbon.
    Updates the system clock, user permissions, database connectivity, and camera feed states.
    """
    def __init__(self, status_bar_frame: ctk.CTkFrame) -> None:
        self.frame = status_bar_frame
        
        # 1. Left container (App details and DB/Camera metrics)
        self.left_panel = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.left_panel.pack(side="left", padx=ThemeManager.PAD_LG, fill="y")
        
        self.version_label = ctk.CTkLabel(
            self.left_panel,
            text="v1.0.0",
            font=ThemeManager.get_font(size=10, weight="bold"),
            text_color=ThemeManager.get_color("text_muted")
        )
        self.version_label.pack(side="left", padx=(0, ThemeManager.PAD_MD))
        
        self.db_label = ctk.CTkLabel(
            self.left_panel,
            text="DB: Connecting...",
            font=ThemeManager.get_font(size=10),
            text_color=ThemeManager.get_color("accent_warning")
        )
        self.db_label.pack(side="left", padx=ThemeManager.PAD_MD)
        
        self.camera_label = ctk.CTkLabel(
            self.left_panel,
            text="Cam: Offline",
            font=ThemeManager.get_font(size=10),
            text_color=ThemeManager.get_color("accent_danger")
        )
        self.camera_label.pack(side="left", padx=ThemeManager.PAD_MD)
        
        self.recognition_label = ctk.CTkLabel(
            self.left_panel,
            text="Engine: Idle",
            font=ThemeManager.get_font(size=10),
            text_color=ThemeManager.get_color("text_muted")
        )
        self.recognition_label.pack(side="left", padx=ThemeManager.PAD_MD)

        # 2. Right container (User tags and Active Clock tracker)
        self.right_panel = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.right_panel.pack(side="right", padx=ThemeManager.PAD_LG, fill="y")
        
        self.user_label = ctk.CTkLabel(
            self.right_panel,
            text="User: Guest",
            font=ThemeManager.get_font(size=10),
            text_color=ThemeManager.get_color("accent_secondary")
        )
        self.user_label.pack(side="left", padx=ThemeManager.PAD_MD)
        
        self.time_label = ctk.CTkLabel(
            self.right_panel,
            text="",
            font=ThemeManager.get_font(size=10),
            text_color=ThemeManager.get_color("text_muted")
        )
        self.time_label.pack(side="left", padx=ThemeManager.PAD_MD)
        
        self.update_time()

    def update_database_status(self, connected: bool, details: str = "") -> None:
        """
        Reflects database driver status.
        """
        if connected:
            self.db_label.configure(
                text=f"DB: Connected ({details})", 
                text_color=ThemeManager.get_color("accent_success")
            )
        else:
            self.db_label.configure(
                text="DB: Offline", 
                text_color=ThemeManager.get_color("accent_danger")
            )

    def update_camera_status(self, status: str, color_key: str = "text_muted") -> None:
        """
        Updates live camera capture metrics.
        """
        self.camera_label.configure(
            text=f"Cam: {status}", 
            text_color=ThemeManager.get_color(color_key)
        )

    def update_recognition_engine(self, status: str, color_key: str = "text_muted") -> None:
        """
        Reflects face detection embedding processor loops.
        """
        self.recognition_label.configure(
            text=f"Engine: {status}", 
            text_color=ThemeManager.get_color(color_key)
        )

    def update_user(self, username: str) -> None:
        """
        Displays credentials of the currently active session user.
        """
        self.user_label.configure(text=f"User: {username}")

    def update_time(self) -> None:
        """
        Event loop hook that checks current OS time and updates status bar label every second.
        """
        now_str = datetime.now().strftime("%H:%M:%S")
        self.time_label.configure(text=now_str)
        self.frame.after(1000, self.update_time)
