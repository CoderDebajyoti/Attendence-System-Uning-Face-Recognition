# ==============================================================================
# Face Recognition Attendance System - Reusable Card & KPI Widgets
# ==============================================================================

import customtkinter as ctk
from src.gui.themes import ThemeManager

class Card(ctk.CTkFrame):
    """
    Base container representing a premium dashboard panel.
    Follows global theme border styles and rounding configurations.
    """
    def __init__(self, master, fg_color=None, border_color=None, border_width=None, corner_radius=None, **kwargs):
        super().__init__(
            master=master,
            fg_color=fg_color or ThemeManager.get_color("bg_card"),
            border_color=border_color or ThemeManager.get_color("border"),
            border_width=border_width if border_width is not None else ThemeManager.BORDER_WIDTH,
            corner_radius=corner_radius if corner_radius is not None else ThemeManager.CORNER_RADIUS_MD,
            **kwargs
        )


class StatisticWidget(Card):
    """
    Key Performance Indicator card containing an icon, large metrics text, 
    and descriptive title with colored status indicators.
    """
    def __init__(self, master, title: str, value: str, icon: str, accent_color: str, **kwargs):
        super().__init__(master=master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        
        # Visual color highlight bar at the top
        self.accent_bar = ctk.CTkFrame(self, height=4, fg_color=accent_color)
        self.accent_bar.place(relx=0, rely=0, relwidth=1)
        
        # Giant Icon label
        self.icon_label = ctk.CTkLabel(
            self, 
            text=icon, 
            font=ThemeManager.get_font(size=24)
        )
        self.icon_label.grid(row=0, column=0, sticky="w", padx=ThemeManager.PAD_LG, pady=(ThemeManager.PAD_LG, 0))
        
        # Dynamic Value
        self.val_label = ctk.CTkLabel(
            self, 
            text=value, 
            font=ThemeManager.get_font(size=22, weight="bold"),
            text_color=ThemeManager.get_color("text_primary")
        )
        self.val_label.grid(row=1, column=0, sticky="w", padx=ThemeManager.PAD_LG, pady=(ThemeManager.PAD_XS, 0))
        
        # Descriptive Title Label
        self.title_label = ctk.CTkLabel(
            self, 
            text=title, 
            font=ThemeManager.get_font(size=12),
            text_color=ThemeManager.get_color("text_muted")
        )
        self.title_label.grid(row=2, column=0, sticky="w", padx=ThemeManager.PAD_LG, pady=(0, ThemeManager.PAD_LG))

    def update_value(self, new_value: str) -> None:
        """
        Dynamically updates the displayed value in the statistic panel.
        """
        self.val_label.configure(text=new_value)
