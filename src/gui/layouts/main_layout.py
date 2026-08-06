# ==============================================================================
# Face Recognition Attendance System - Main Layout Manager
# ==============================================================================

import customtkinter as ctk
from src.gui.themes import ThemeManager

class MainLayout:
    """
    Layout Manager responsible for setting up the primary split-pane frames:
    - Sidebar (fixed width navigation column on the left)
    - Header (top dashboard status ribbon)
    - Page Container (viewport card presenting active layouts)
    - Status Bar (diagnostics monitor ribbon at the bottom)
    """
    def __init__(self, root: ctk.CTk):
        self.root = root
        
        # Configure layout root columns
        self.root.grid_columnconfigure(0, weight=0) # Sidebar column (fixed width)
        self.root.grid_columnconfigure(1, weight=1) # Content area column (scales)
        self.root.grid_rowconfigure(0, weight=1)
        
        self.create_sidebar()
        self.create_main_container()

    def create_sidebar(self) -> None:
        """
        Builds the left-hand navigation sidebar containing menu buttons and theme selectors.
        """
        self.sidebar = ctk.CTkFrame(
            self.root, 
            width=230, 
            fg_color=ThemeManager.get_color("bg_sidebar"), 
            corner_radius=0,
            border_color=ThemeManager.get_color("border"),
            border_width=0
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(2, weight=1) # Flexible space between menu and footer
        
        # 1. Sidebar Header (Logo and Branding)
        header_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=ThemeManager.PAD_LG, pady=(ThemeManager.PAD_XL, ThemeManager.PAD_LG))
        
        logo = ctk.CTkLabel(header_frame, text="🛡️", font=ThemeManager.get_font(size=24))
        logo.pack(side="left", padx=(0, ThemeManager.PAD_SM))
        
        brand_name = ctk.CTkLabel(
            header_frame, 
            text="ATTENDANCE AI", 
            font=ThemeManager.get_font(size=14, weight="bold"),
            text_color=ThemeManager.get_color("accent_primary")
        )
        brand_name.pack(side="left")
        
        # Divider Line
        divider = ctk.CTkFrame(self.sidebar, height=1, fg_color=ThemeManager.get_color("border"))
        divider.grid(row=1, column=0, sticky="ew", padx=ThemeManager.PAD_LG, pady=(0, ThemeManager.PAD_MD))
        
        # 2. Navigation Menu Scroll Area
        self.nav_scroll_frame = ctk.CTkScrollableFrame(
            self.sidebar, 
            fg_color="transparent", 
            scrollbar_button_color=ThemeManager.get_color("bg_active")
        )
        self.nav_scroll_frame.grid(row=2, column=0, sticky="nsew", padx=ThemeManager.PAD_SM, pady=0)
        self.nav_scroll_frame.grid_columnconfigure(0, weight=1)
        
        # 3. Sidebar Footer
        self.sidebar_footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.sidebar_footer.grid(row=3, column=0, sticky="ew", padx=ThemeManager.PAD_LG, pady=ThemeManager.PAD_LG)

    def create_main_container(self) -> None:
        """
        Creates the main workspace layout (Header, Page Container, Status Bar).
        """
        self.main_container = ctk.CTkFrame(self.root, fg_color=ThemeManager.get_color("bg_main"), corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1) # Page viewport expands to fill space
        
        # 1. Top Header Area
        self.header = ctk.CTkFrame(
            self.main_container, 
            height=60, 
            fg_color=ThemeManager.get_color("bg_header"), 
            corner_radius=0,
            border_color=ThemeManager.get_color("border"),
            border_width=0
        )
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_propagate(False)
        self.header.grid_columnconfigure(0, weight=1)
        
        # Breadcrumbs (tracked and updated by NavigationManager)
        self.breadcrumb_label = ctk.CTkLabel(
            self.header, 
            text="System / Dashboard", 
            font=ThemeManager.get_font(size=13, weight="bold"),
            text_color=ThemeManager.get_color("text_muted")
        )
        self.breadcrumb_label.grid(row=0, column=0, sticky="w", padx=ThemeManager.PAD_XL, pady=18)
        
        # Status details (Date & System connection)
        from datetime import datetime
        self.status_detail_label = ctk.CTkLabel(
            self.header,
            text=f"Server Live | {datetime.now().strftime('%Y-%b-%d')}",
            font=ThemeManager.get_font(size=12),
            text_color=ThemeManager.get_color("accent_success")
        )
        self.status_detail_label.grid(row=0, column=1, sticky="e", padx=ThemeManager.PAD_XL, pady=18)
        
        # 2. Dynamic Page View Frame Container
        self.page_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.page_container.grid(row=1, column=0, sticky="nsew")
        self.page_container.grid_columnconfigure(0, weight=1)
        self.page_container.grid_rowconfigure(0, weight=1)
        
        # 3. Status Bar Bottom Panel
        self.status_bar = ctk.CTkFrame(
            self.main_container, 
            height=26, 
            fg_color=ThemeManager.get_color("bg_header"), 
            corner_radius=0
        )
        self.status_bar.grid(row=2, column=0, sticky="ew")
        self.status_bar.grid_propagate(False)
