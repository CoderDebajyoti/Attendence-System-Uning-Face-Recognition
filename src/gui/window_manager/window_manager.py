# ==============================================================================
# Face Recognition Attendance System - Window Manager
# ==============================================================================

import customtkinter as ctk
from src.core import constants

class WindowManager:
    """
    Manages top-level window scaling, positioning, min/max constraints, 
    and centering coordinate logic on different physical display profiles.
    """
    
    @staticmethod
    def initialize_window(window: ctk.CTk, title: str, width: int = 1200, height: int = 800) -> None:
        """
        Applies system constraints, min size limits, titles, and centers window.
        """
        window.title(title)
        window.geometry(f"{width}x{height}")
        window.minsize(constants.WINDOW_MIN_WIDTH, constants.WINDOW_MIN_HEIGHT)
        WindowManager.center_on_screen(window, width, height)

    @staticmethod
    def center_on_screen(window: ctk.CTk, width: int, height: int) -> None:
        """
        Aligns window grid to center bounds of the current display monitor.
        """
        window.update_idletasks()
        s_w = window.winfo_screenwidth()
        s_h = window.winfo_screenheight()
        
        # Calculate coordinates for center mapping
        x = (s_w - width) // 2
        y = (s_h - height) // 2
        
        window.geometry(f"{width}x{height}+{x}+{y}")
