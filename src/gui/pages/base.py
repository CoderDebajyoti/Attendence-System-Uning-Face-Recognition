# ==============================================================================
# Face Recognition Attendance System - Base Page Class
# ==============================================================================

import customtkinter as ctk
from src.gui.themes import ThemeManager

class BasePage(ctk.CTkFrame):
    """
    Abstract base page view class. All navigation page views subclass this frame
    to inherit consistent layout structures and phase markings.
    """
    def __init__(self, parent, controller, title: str, description: str, phase: int) -> None:
        super().__init__(parent, fg_color=ThemeManager.get_color("bg_main"))
        self.controller = controller
        self.title_text = title
        self.description_text = description
        self.phase = phase
        
        # Grid weights setup
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # 1. Page Header Area
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=ThemeManager.PAD_XL, pady=(ThemeManager.PAD_XL, ThemeManager.PAD_MD))
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text=self.title_text, 
            font=ThemeManager.get_font(size=24, weight="bold"),
            text_color=ThemeManager.get_color("text_primary")
        )
        self.title_label.grid(row=0, column=0, sticky="w")
        
        # Description
        self.desc_label = ctk.CTkLabel(
            self.header_frame, 
            text=self.description_text, 
            font=ThemeManager.get_font(size=13),
            text_color=ThemeManager.get_color("text_muted"),
            wraplength=700,
            justify="left"
        )
        self.desc_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(ThemeManager.PAD_XS, 0))
        
        # 2. Horizontal Divider
        self.divider = ctk.CTkFrame(self, height=1, fg_color=ThemeManager.get_color("border"))
        self.divider.grid(row=1, column=0, sticky="ew", padx=ThemeManager.PAD_XL, pady=(0, ThemeManager.PAD_MD))
        
        # 3. Main Content Area (Subclasses override this by packing/gridding inside self.content_frame)
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=2, column=0, sticky="nsew", padx=ThemeManager.PAD_XL, pady=(0, ThemeManager.PAD_XL))
        
        # Default placeholder if no content is added
        self.show_default_placeholder()

    def show_default_placeholder(self) -> None:
        """
        Creates a placeholder overlay when sub-pages are not yet completed.
        """
        # Configure layout inside content area
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        card = ctk.CTkFrame(
            self.content_frame, 
            fg_color=ThemeManager.get_color("bg_card"),
            border_color=ThemeManager.get_color("border"),
            border_width=ThemeManager.BORDER_WIDTH,
            corner_radius=ThemeManager.CORNER_RADIUS_LG
        )
        card.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)
        
        inner_content = ctk.CTkFrame(card, fg_color="transparent")
        inner_content.grid(row=0, column=0)
        
        # Giant Icon label placeholder
        icon_label = ctk.CTkLabel(
            inner_content, 
            text="✨", 
            font=ThemeManager.get_font(size=56)
        )
        icon_label.pack(pady=10)
        
        status_header = ctk.CTkLabel(
            inner_content,
            text="Feature Under Development",
            font=ThemeManager.get_font(size=18, weight="bold"),
            text_color=ThemeManager.get_color("text_primary")
        )
        status_header.pack(pady=5)
        
        status_sub = ctk.CTkLabel(
            inner_content,
            text=f"The structural layout for this view is ready.\nThe backend services and UI elements will be integrated during future phases.",
            font=ThemeManager.get_font(size=12),
            text_color=ThemeManager.get_color("text_muted"),
            justify="center"
        )
        status_sub.pack(pady=10)
        
        coming_soon_badge = ctk.CTkLabel(
            inner_content,
            text="COMING SOON",
            font=ThemeManager.get_font(size=11, weight="bold"),
            text_color=ThemeManager.get_color("text_dark"),
            fg_color=ThemeManager.get_color("accent_primary"),
            corner_radius=ThemeManager.CORNER_RADIUS_SM,
            width=110,
            height=26
        )
        coming_soon_badge.pack(pady=5)
