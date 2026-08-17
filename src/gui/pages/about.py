# ==============================================================================
# Face Recognition Attendance System - About Page View
# ==============================================================================

import customtkinter as ctk
from src.gui.pages.base import BasePage
from src.gui.themes import ThemeManager
from src.gui.components import Card

class AboutPage(BasePage):
    """
    About Page View. Displays system version parameters, tech stack metrics,
    and institutional release statements.
    """
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            title="About System",
            description="Version information, system architecture status, and license details.",
            phase=1
        )

    def show_default_placeholder(self) -> None:
        """
        Overrides base placeholder to render system statistics.
        """
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Scrollable container
        self.scroll_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        self.scroll_frame.grid(row=0, column=0, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        # 1. Main Branding Card
        brand_card = Card(self.scroll_frame)
        brand_card.pack(fill="x", padx=10, pady=10)
        brand_card.grid_columnconfigure(0, weight=1)

        logo = ctk.CTkLabel(brand_card, text="🛡️", font=ThemeManager.get_font(size=48))
        logo.pack(pady=(20, 10))

        title = ctk.CTkLabel(
            brand_card,
            text="Face Recognition Attendance System",
            font=ThemeManager.get_font(size=18, weight="bold"),
            text_color=ThemeManager.get_color("text_primary")
        )
        title.pack()

        version = ctk.CTkLabel(
            brand_card,
            text="Version 1.0.0 (Stable Release Build)",
            font=ThemeManager.get_font(size=12, weight="bold"),
            text_color=ThemeManager.get_color("accent_primary")
        )
        version.pack(pady=(2, 10))

        desc = ctk.CTkLabel(
            brand_card,
            text="A secure local-first biometrics desktop application designed to track and manage student check-in "
                 "registries automatically. Utilizes high-precision face recognition Haar Cascade classifiers, "
                 "Local Binary Patterns Histograms (LBPH) training, and transaction-safe SQLAlchemy database repositories.",
            font=ThemeManager.get_font(size=12),
            text_color=ThemeManager.get_color("text_light"),
            wraplength=600,
            justify="center"
        )
        desc.pack(padx=20, pady=(0, 20))

        # 2. Technology Stack Card
        tech_card = Card(self.scroll_frame)
        tech_card.pack(fill="x", padx=10, pady=10)
        tech_card.grid_columnconfigure(1, weight=1)

        tech_title = ctk.CTkLabel(
            tech_card,
            text="System Technology Stack & Modules",
            font=ThemeManager.get_font(size=13, weight="bold"),
            text_color=ThemeManager.get_color("accent_secondary")
        )
        tech_title.grid(row=0, column=0, columnspan=2, sticky="w", padx=ThemeManager.PAD_LG, pady=ThemeManager.PAD_MD)

        tech_stack = [
            ("Core Programming Framework", "Python v3.12 (Virtual Environment Executable Runtime)"),
            ("Graphical User Interface", "CustomTkinter v5.2.0 (Modernized Tkinter Layout Bindings)"),
            ("Computer Vision Engine", "OpenCV v4.9 (Haar Cascade Face Detectors & LBPH Local Match Recognizers)"),
            ("Database Mapping & Models", "SQLAlchemy v2.0 (ORM wrapper mapping SQLite transactional repositories)"),
            ("Password Hashing & Crypt", "Bcrypt v4.1 (Blowfish-based salt-hashed cryptographic administrators)"),
            ("Reports Spreadsheet Exports", "OpenPyXL v3.1 (Dynamic XML multi-sheet workbook generation)")
        ]

        for idx, (component, detail) in enumerate(tech_stack):
            comp_lbl = ctk.CTkLabel(tech_card, text=component, font=ThemeManager.get_font(size=11, weight="bold"), text_color=ThemeManager.get_color("text_light"))
            comp_lbl.grid(row=idx+1, column=0, sticky="w", padx=ThemeManager.PAD_LG, pady=ThemeManager.PAD_XS)
            
            det_lbl = ctk.CTkLabel(tech_card, text=detail, font=ThemeManager.get_font(size=11), text_color=ThemeManager.get_color("text_muted"))
            det_lbl.grid(row=idx+1, column=1, sticky="w", padx=ThemeManager.PAD_LG, pady=ThemeManager.PAD_XS)

        # 3. Copyright Notice
        copyright_lbl = ctk.CTkLabel(
            self.scroll_frame,
            text="© 2026 Face Recognition Attendance System. All rights reserved. Locally Secured.",
            font=ThemeManager.get_font(size=10),
            text_color=ThemeManager.get_color("text_muted")
        )
        copyright_lbl.pack(pady=20)
