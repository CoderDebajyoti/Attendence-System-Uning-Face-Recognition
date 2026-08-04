# ==============================================================================
# Face Recognition Attendance System - Base Page class
# ==============================================================================

import customtkinter as ctk
from src.gui.theme import Theme

class BasePage(ctk.CTkFrame):
    """
    Abstract base page view class. All navigation page views subclass this frame
    to inherit consistent layout structures and phase markings.
    """
    def __init__(self, parent, controller, title: str, description: str, phase: int):
        super().__init__(parent, fg_color=Theme.BG_MAIN)
        self.controller = controller
        self.title = title
        self.description = description
        self.phase = phase
        
        # Grid weights setup
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # 1. Page Header Area
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=Theme.PAD_XL, pady=(Theme.PAD_XL, Theme.PAD_MD))
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text=self.title, 
            font=Theme.get_font(size=24, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        self.title_label.grid(row=0, column=0, sticky="w")
        
        # Development Phase Tag
        self.phase_tag = ctk.CTkLabel(
            self.header_frame,
            text=f"Phase {self.phase} Design",
            font=Theme.get_font(size=11, weight="bold"),
            fg_color=Theme.BG_ACTIVE,
            text_color=Theme.ACCENT_PRIMARY,
            corner_radius=Theme.CORNER_RADIUS_SM,
            width=90,
            height=24
        )
        self.phase_tag.grid(row=0, column=1, sticky="e")
        
        # Description
        self.desc_label = ctk.CTkLabel(
            self.header_frame, 
            text=self.description, 
            font=Theme.get_font(size=13),
            text_color=Theme.TEXT_MUTED,
            wraplength=700,
            justify="left"
        )
        self.desc_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(Theme.PAD_XS, 0))
        
        # 2. Horizontal Divider
        self.divider = ctk.CTkFrame(self, height=1, fg_color=Theme.BORDER_COLOR)
        self.divider.grid(row=1, column=0, sticky="ew", padx=Theme.PAD_XL, pady=(0, Theme.PAD_MD))
        
        # 3. Main Content Area (Subclasses override this by packing/gridding inside self.content_frame)
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=2, column=0, sticky="nsew", padx=Theme.PAD_XL, pady=(0, Theme.PAD_XL))
        
        # Default placeholder if no content is added
        self.show_default_placeholder()

    def show_default_placeholder(self) -> None:
        """
        Creates a beautiful placeholder overlay when sub-pages are not yet completed.
        """
        # Configure layout inside content area
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        card = ctk.CTkFrame(
            self.content_frame, 
            fg_color=Theme.BG_CARD,
            border_color=Theme.BORDER_COLOR,
            border_width=Theme.BORDER_WIDTH,
            corner_radius=Theme.CORNER_RADIUS_LG
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
            font=Theme.get_font(size=56)
        )
        icon_label.pack(pady=10)
        
        status_header = ctk.CTkLabel(
            inner_content,
            text="Feature Under Development",
            font=Theme.get_font(size=18, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        status_header.pack(pady=5)
        
        status_sub = ctk.CTkLabel(
            inner_content,
            text=f"The structural layout for this view is ready.\nThe backend services and UI elements will be integrated during Phase {self.phase + 1}.",
            font=Theme.get_font(size=12),
            text_color=Theme.TEXT_MUTED,
            justify="center"
        )
        status_sub.pack(pady=10)
        
        coming_soon_badge = ctk.CTkLabel(
            inner_content,
            text="COMING SOON",
            font=Theme.get_font(size=11, weight="bold"),
            text_color=Theme.TEXT_DARK,
            fg_color=Theme.ACCENT_PRIMARY,
            corner_radius=Theme.CORNER_RADIUS_SM,
            width=110,
            height=26
        )
        coming_soon_badge.pack(pady=5)
