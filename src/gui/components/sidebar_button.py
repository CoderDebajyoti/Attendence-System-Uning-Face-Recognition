# ==============================================================================
# Face Recognition Attendance System - Sidebar Button Component
# ==============================================================================

import customtkinter as ctk
from src.gui.themes import ThemeManager

class SidebarButton(ctk.CTkButton):
    """
    Styled button designed specifically for left-panel sidebar navigation.
    Maintains toggle states and premium visual indicators.
    """
    def __init__(self, master, text: str, icon: str, command, **kwargs):
        self.raw_text = text
        self.icon = icon
        
        super().__init__(
            master=master,
            text=f"  {icon}  {text}",
            anchor="w",
            font=ThemeManager.get_font(size=13, weight="normal"),
            fg_color="transparent",
            text_color=ThemeManager.get_color("text_light"),
            hover_color=ThemeManager.get_color("bg_active"),
            corner_radius=ThemeManager.CORNER_RADIUS_SM,
            height=38,
            command=command,
            **kwargs
        )

    def set_active(self, active: bool) -> None:
        """
        Switches button style state between active/inactive.
        """
        if active:
            self.configure(
                fg_color=ThemeManager.get_color("bg_active"),
                text_color=ThemeManager.get_color("accent_primary"),
                font=ThemeManager.get_font(size=13, weight="bold")
            )
        else:
            self.configure(
                fg_color="transparent",
                text_color=ThemeManager.get_color("text_light"),
                font=ThemeManager.get_font(size=13, weight="normal")
            )
