# ==============================================================================
# Face Recognition Attendance System - Theme & Token Manager
# ==============================================================================

import customtkinter as ctk

class ThemeManager:
    """
    Manages layout tokens, sizing ratios, fonts, icons, and HSL-mapped color schemes
    supporting Dark and Light runtime styling.
    """
    
    # Appearance Modes
    MODE_DARK = "dark"
    MODE_LIGHT = "light"
    MODE_SYSTEM = "system"

    # Color Palette: Dark Mode (Catppuccin Mocha-inspired premium palette)
    PALETTE_DARK = {
        "bg_main": "#1e1e2e",
        "bg_sidebar": "#11111b",
        "bg_header": "#181825",
        "bg_card": "#252538",
        "bg_active": "#313244",
        "border": "#313244",
        "accent_primary": "#cba6f7",     # Soft Purple
        "accent_secondary": "#89b4fa",   # Light Blue
        "accent_success": "#a6e3a1",     # Soft Green
        "accent_warning": "#f9e2af",     # Pastel Yellow
        "accent_danger": "#f38ba8",      # Pastel Red
        "text_primary": "#cdd6f4",       # Readable text
        "text_muted": "#a6adc8",         # Descriptions
        "text_light": "#bac2de",         # Bright labels
        "text_dark": "#11111b"           # High contrast text for buttons
    }

    # Color Palette: Light Mode (Clean Slate & Violet palette)
    PALETTE_LIGHT = {
        "bg_main": "#f2f2f7",
        "bg_sidebar": "#ffffff",
        "bg_header": "#ffffff",
        "bg_card": "#e5e5ea",
        "bg_active": "#d1d1d6",
        "border": "#c7c7cc",
        "accent_primary": "#8e2de2",     # Royal Purple
        "accent_secondary": "#4a90e2",   # Vibrant Blue
        "accent_success": "#34c759",     # IOS Green
        "accent_warning": "#ffcc00",     # Amber Yellow
        "accent_danger": "#ff3b30",      # IOS Red
        "text_primary": "#1c1c1e",       # Dark text
        "text_muted": "#8e8e93",         # Muted description text
        "text_light": "#3a3a3c",         # Soft dark label text
        "text_dark": "#ffffff"           # High contrast light text for buttons
    }

    # Spacing and Dimension Tokens
    PAD_XS = 4
    PAD_SM = 8
    PAD_MD = 12
    PAD_LG = 16
    PAD_XL = 24

    CORNER_RADIUS_SM = 6
    CORNER_RADIUS_MD = 10
    CORNER_RADIUS_LG = 16

    BORDER_WIDTH = 1

    # Typography Font Configurations
    FONT_FAMILY = "Segoe UI"

    _current_mode = MODE_DARK

    @classmethod
    def set_appearance_mode(cls, mode: str) -> None:
        """
        Updates the global appearance mode.
        """
        clean_mode = mode.lower()
        if clean_mode in [cls.MODE_DARK, cls.MODE_LIGHT, cls.MODE_SYSTEM]:
            ctk.set_appearance_mode(clean_mode)
            if clean_mode != cls.MODE_SYSTEM:
                cls._current_mode = clean_mode
            else:
                cls._current_mode = ctk.get_appearance_mode().lower()

    @classmethod
    def get_color(cls, color_key: str) -> str:
        """
        Fetches the color value corresponding to the current appearance mode.
        """
        palette = cls.PALETTE_DARK if cls._current_mode == cls.MODE_DARK else cls.PALETTE_LIGHT
        return palette.get(color_key, "#ffffff")

    @classmethod
    def get_font(cls, size: int = 12, weight: str = "normal", slant: str = "roman") -> ctk.CTkFont:
        """
        Returns a customized ctk.CTkFont instance.
        """
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=size, weight=weight, slant=slant)

    # Standard Theme-Compatible Class Attributes to mirror the old theme
    @property
    def BG_MAIN(self): return self.get_color("bg_main")
    @property
    def BG_SIDEBAR(self): return self.get_color("bg_sidebar")
    @property
    def BG_HEADER(self): return self.get_color("bg_header")
    @property
    def BG_CARD(self): return self.get_color("bg_card")
    @property
    def BG_ACTIVE(self): return self.get_color("bg_active")
    @property
    def BORDER_COLOR(self): return self.get_color("border")
    
    @property
    def ACCENT_PRIMARY(self): return self.get_color("accent_primary")
    @property
    def ACCENT_SECONDARY(self): return self.get_color("accent_secondary")
    @property
    def ACCENT_SUCCESS(self): return self.get_color("accent_success")
    @property
    def ACCENT_WARNING(self): return self.get_color("accent_warning")
    @property
    def ACCENT_DANGER(self): return self.get_color("accent_danger")
    
    @property
    def TEXT_PRIMARY(self): return self.get_color("text_primary")
    @property
    def TEXT_MUTED(self): return self.get_color("text_muted")
    @property
    def TEXT_LIGHT(self): return self.get_color("text_light")
    @property
    def TEXT_DARK(self): return self.get_color("text_dark")
