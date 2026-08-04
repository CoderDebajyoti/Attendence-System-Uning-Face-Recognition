# ==============================================================================
# Face Recognition Attendance System - UI Color Palette & Typography Theme
# ==============================================================================

import customtkinter as ctk

class Theme:
    """
    Defines UI styling parameters, including an HSL-tailored dark mode color palette,
    borders, spacing, and fonts.
    """
    # Color Palette (Catppuccin Mocha-inspired premium slate/violet palette)
    BG_MAIN = "#1e1e2e"          # Sleek dark slate canvas
    BG_SIDEBAR = "#11111b"       # Deep dark sidebar panel
    BG_HEADER = "#181825"        # Soft dark top header panel
    BG_CARD = "#252538"          # Lighter slate card/widget backgrounds
    BG_ACTIVE = "#313244"        # Active button/item highlights
    
    # Accent Colors
    ACCENT_PRIMARY = "#cba6f7"   # Premium Soft Purple / Violet
    ACCENT_SECONDARY = "#89b4fa" # High-contrast Light Blue
    ACCENT_SUCCESS = "#a6e3a1"   # Soft Emerald Green
    ACCENT_WARNING = "#f9e2af"   # Pastel Yellow
    ACCENT_DANGER = "#f38ba8"    # Soft Pastel Red
    
    # Text Colors
    TEXT_PRIMARY = "#cdd6f4"     # Bright readable text
    TEXT_MUTED = "#a6adc8"       # Secondary/disabled description labels
    TEXT_LIGHT = "#bac2de"       # Subtle white labels
    TEXT_DARK = "#11111b"        # Contrasting text for bright accents
    
    # Borders & Corners
    CORNER_RADIUS_SM = 6
    CORNER_RADIUS_MD = 10
    CORNER_RADIUS_LG = 16
    
    BORDER_COLOR = "#313244"
    BORDER_WIDTH = 1
    
    # Spacing Tokens
    PAD_XS = 4
    PAD_SM = 8
    PAD_MD = 12
    PAD_LG = 16
    PAD_XL = 24

    # Typography Font Configurations
    FONT_FAMILY = "Segoe UI"
    
    @classmethod
    def get_font(cls, size: int = 12, weight: str = "normal", slant: str = "roman") -> ctk.CTkFont:
        """
        Helper method returning a ctk.CTkFont instance.
        """
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=size, weight=weight, slant=slant)
