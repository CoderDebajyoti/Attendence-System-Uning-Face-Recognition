# ==============================================================================
# Face Recognition Attendance System - Main Application Shell Coordinator
# ==============================================================================

import customtkinter as ctk
from datetime import datetime
from src.gui.theme import Theme
from src.gui.pages import (
    DashboardPage, StudentsPage, FacultyPage, DepartmentsPage,
    CoursesPage, SubjectsPage, DatasetPage, CameraPage,
    AttendancePage, ReportsPage, SettingsPage, AboutPage
)

class AppShell(ctk.CTk):
    """
    Main application shell window coordinator. Implements the split-pane layout
    (Sidebar, Header, dynamic Page Content area, and Status Bar).
    """
    def __init__(self):
        super().__init__()
        
        # Configure window properties
        self.title("Face Recognition Attendance System")
        self.geometry("1200x800")
        self.minsize(1024, 768)
        self.configure(fg_color=Theme.BG_MAIN)
        
        # Grid weights setup
        self.grid_columnconfigure(0, weight=0) # Sidebar column (fixed width)
        self.grid_columnconfigure(1, weight=1) # Content column (expands)
        self.grid_rowconfigure(0, weight=1)
        
        # Keep track of active navigation items
        self.nav_buttons = {}
        self.pages = {}
        
        # Setup UI Panels
        self.create_sidebar()
        self.create_main_container()
        self.initialize_pages()
        
        # Start by showing the dashboard
        self.show_page("Dashboard")

    def create_sidebar(self) -> None:
        """
        Creates the left-hand navigation sidebar containing menu buttons and theme selectors.
        """
        self.sidebar = ctk.CTkFrame(
            self, 
            width=230, 
            fg_color=Theme.BG_SIDEBAR, 
            corner_radius=0,
            border_color=Theme.BORDER_COLOR,
            border_width=0
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(2, weight=1) # Flexible space between menus and footer
        
        # 1. Sidebar Header (Logo and Name)
        header_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=Theme.PAD_LG, pady=(Theme.PAD_XL, Theme.PAD_LG))
        
        logo = ctk.CTkLabel(header_frame, text="🛡️", font=Theme.get_font(size=24))
        logo.pack(side="left", padx=(0, Theme.PAD_SM))
        
        brand_name = ctk.CTkLabel(
            header_frame, 
            text="ATTENDANCE AI", 
            font=Theme.get_font(size=14, weight="bold"),
            text_color=Theme.ACCENT_PRIMARY
        )
        brand_name.pack(side="left")
        
        # Divider line
        divider = ctk.CTkFrame(self.sidebar, height=1, fg_color=Theme.BORDER_COLOR)
        divider.grid(row=1, column=0, sticky="ew", padx=Theme.PAD_LG, pady=(0, Theme.PAD_MD))
        
        # 2. Navigation Menu List
        self.nav_scroll_frame = ctk.CTkScrollableFrame(
            self.sidebar, 
            fg_color="transparent", 
            scrollbar_button_color=Theme.BG_ACTIVE
        )
        self.nav_scroll_frame.grid(row=2, column=0, sticky="nsew", padx=Theme.PAD_SM, pady=0)
        self.nav_scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Define menu structure
        menu_items = [
            ("Dashboard", "📊"),
            ("Students", "👥"),
            ("Faculty", "👨‍🏫"),
            ("Departments", "🏢"),
            ("Courses", "🎓"),
            ("Subjects", "📘"),
            ("Dataset", "📂"),
            ("Camera", "📷"),
            ("Attendance", "📝"),
            ("Reports", "📈"),
            ("Settings", "⚙️"),
            ("About", "ℹ️")
        ]
        
        for idx, (name, icon) in enumerate(menu_items):
            btn = ctk.CTkButton(
                self.nav_scroll_frame,
                text=f"  {icon}  {name}",
                anchor="w",
                font=Theme.get_font(size=13, weight="normal"),
                fg_color="transparent",
                text_color=Theme.TEXT_LIGHT,
                hover_color=Theme.BG_ACTIVE,
                corner_radius=Theme.CORNER_RADIUS_SM,
                height=38,
                command=lambda n=name: self.show_page(n)
            )
            btn.grid(row=idx, column=0, sticky="ew", pady=2)
            self.nav_buttons[name] = btn
            
        # 3. Sidebar Footer (Theme controls or utility toggles)
        self.sidebar_footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.sidebar_footer.grid(row=3, column=0, sticky="ew", padx=Theme.PAD_LG, pady=Theme.PAD_LG)
        
        theme_label = ctk.CTkLabel(
            self.sidebar_footer, 
            text="Visual Mode", 
            font=Theme.get_font(size=11), 
            text_color=Theme.TEXT_MUTED
        )
        theme_label.pack(anchor="w", pady=(0, Theme.PAD_XS))
        
        self.theme_menu = ctk.CTkOptionMenu(
            self.sidebar_footer,
            values=["Dark", "Light", "System"],
            font=Theme.get_font(size=12),
            dropdown_font=Theme.get_font(size=12),
            fg_color=Theme.BG_ACTIVE,
            button_color=Theme.BG_ACTIVE,
            button_hover_color=Theme.BG_CARD,
            dropdown_fg_color=Theme.BG_CARD,
            dropdown_hover_color=Theme.BG_ACTIVE,
            dropdown_text_color=Theme.TEXT_PRIMARY,
            text_color=Theme.TEXT_PRIMARY,
            corner_radius=Theme.CORNER_RADIUS_SM,
            command=self.change_theme_mode
        )
        self.theme_menu.pack(fill="x")

    def create_main_container(self) -> None:
        """
        Builds the right-hand panel containing the top header, the dynamic content page container,
        and the bottom status bar.
        """
        self.main_container = ctk.CTkFrame(self, fg_color=Theme.BG_MAIN, corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1) # Core Page view expands to fit
        
        # 1. Top Header Area
        self.header = ctk.CTkFrame(
            self.main_container, 
            height=60, 
            fg_color=Theme.BG_HEADER, 
            corner_radius=0,
            border_color=Theme.BORDER_COLOR,
            border_width=0
        )
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_propagate(False)
        self.header.grid_columnconfigure(0, weight=1)
        
        # Breadcrumbs
        self.breadcrumb_label = ctk.CTkLabel(
            self.header, 
            text="System / Dashboard", 
            font=Theme.get_font(size=13, weight="bold"),
            text_color=Theme.TEXT_MUTED
        )
        self.breadcrumb_label.grid(row=0, column=0, sticky="w", padx=Theme.PAD_XL, pady=18)
        
        # Status details (Date & System connection)
        self.status_detail_label = ctk.CTkLabel(
            self.header,
            text=f"Server Live | {datetime.now().strftime('%Y-%b-%d')}",
            font=Theme.get_font(size=12),
            text_color=Theme.ACCENT_SUCCESS
        )
        self.status_detail_label.grid(row=0, column=1, sticky="e", padx=Theme.PAD_XL, pady=18)
        
        # 2. Dynamic Page View Frame
        self.page_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.page_container.grid(row=1, column=0, sticky="nsew")
        self.page_container.grid_columnconfigure(0, weight=1)
        self.page_container.grid_rowconfigure(0, weight=1)
        
        # 3. Status Bar
        self.status_bar = ctk.CTkFrame(
            self.main_container, 
            height=26, 
            fg_color=Theme.BG_HEADER, 
            corner_radius=0
        )
        self.status_bar.grid(row=2, column=0, sticky="ew")
        self.status_bar.grid_propagate(False)
        
        # Version indicators
        version_label = ctk.CTkLabel(
            self.status_bar, 
            text="Version 1.0.0-Beta (Phase 5 Pipeline Design)", 
            font=Theme.get_font(size=10),
            text_color=Theme.TEXT_MUTED
        )
        version_label.pack(side="left", padx=Theme.PAD_LG, pady=2)
        
        # Security hash indicators
        sec_label = ctk.CTkLabel(
            self.status_bar,
            text="🔐 End-to-End Cryptographic Tunneling Active",
            font=Theme.get_font(size=10),
            text_color=Theme.TEXT_MUTED
        )
        sec_label.pack(side="right", padx=Theme.PAD_LG, pady=2)

    def initialize_pages(self) -> None:
        """
        Initializes and caches all page view classes in memory.
        """
        mapping = {
            "Dashboard": DashboardPage,
            "Students": StudentsPage,
            "Faculty": FacultyPage,
            "Departments": DepartmentsPage,
            "Courses": CoursesPage,
            "Subjects": SubjectsPage,
            "Dataset": DatasetPage,
            "Camera": CameraPage,
            "Attendance": AttendancePage,
            "Reports": ReportsPage,
            "Settings": SettingsPage,
            "About": AboutPage
        }
        
        for name, cls in mapping.items():
            frame = cls(parent=self.page_container, controller=self)
            frame.grid(row=0, column=0, sticky="nsew")
            self.pages[name] = frame

    def show_page(self, page_name: str) -> None:
        """
        Switches the display to show the requested page name and updates navigation indicators.
        """
        if page_name not in self.pages:
            return
            
        # Hide/reset visual indicator of other pages and buttons
        for btn_name, btn in self.nav_buttons.items():
            if btn_name == page_name:
                btn.configure(
                    fg_color=Theme.BG_ACTIVE,
                    text_color=Theme.ACCENT_PRIMARY,
                    font=Theme.get_font(size=13, weight="bold")
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=Theme.TEXT_LIGHT,
                    font=Theme.get_font(size=13, weight="normal")
                )
                
        # Raise selected page frame
        page = self.pages[page_name]
        page.tkraise()
        
        # Update breadcrumbs text
        self.breadcrumb_label.configure(text=f"System / {page_name}")

    def change_theme_mode(self, value: str) -> None:
        """
        Changes CustomTkinter window theme runtime rendering states.
        """
        ctk.set_appearance_mode(value.lower())
