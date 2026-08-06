# ==============================================================================
# Face Recognition Attendance System - Main Application Shell Coordinator
# ==============================================================================

import customtkinter as ctk
from src.gui.themes import ThemeManager
from src.gui.window_manager import WindowManager
from src.gui.layouts import MainLayout
from src.gui.pages import (
    PageManager, DashboardPage, StudentsPage, FacultyPage, DepartmentsPage,
    CoursesPage, SubjectsPage, DatasetPage, CameraPage,
    AttendancePage, ReportsPage, SettingsPage, AboutPage
)
from src.gui.navigation import NavigationManager
from src.gui.status_manager import StatusManager
from src.gui.components import SidebarButton

class AppShell(ctk.CTk):
    """
    Main application shell window coordinator. Implements modular framework
    by composing Layout, Navigation, Page, Theme, Window, and Status managers.
    """
    def __init__(self, settings) -> None:
        super().__init__()
        self.settings = settings
        
        # 1. Initialize Window geometry, constraints, and centering
        WindowManager.initialize_window(self, "Face Recognition Attendance System")
        
        # 2. Setup appearance mode based on settings
        ThemeManager.set_appearance_mode("dark")
        
        # 3. Create Main Layout frames (Sidebar, Header, Content Area, Status Bar)
        self.layout = MainLayout(self)
        
        # 4. Instantiate Page Manager
        self.page_manager = PageManager(self.layout.page_container, self)
        
        # 5. Register all available page classes
        self.register_application_pages()
        
        # 6. Instantiate Status Bar Manager and seed variables
        self.status_manager = StatusManager(self.layout.status_bar)
        self.initialize_status_metrics()
        
        # 7. Instantiate Navigation Manager
        self.navigation_manager = NavigationManager(
            layout=self.layout, 
            page_manager=self.page_manager, 
            header_label=self.layout.breadcrumb_label
        )
        
        # 8. Render and hook up sidebar menu items
        self.create_navigation_menu()
        self.create_theme_selector()
        
        # 9. Load dashboard view initially
        self.navigation_manager.show_page("Dashboard")

    def register_application_pages(self) -> None:
        """
        Registers all lazy-instantiated pages with the Page Manager registry.
        """
        pages_registry = {
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
        for name, cls in pages_registry.items():
            self.page_manager.register_page(name, cls)

    def create_navigation_menu(self) -> None:
        """
        Builds the navigation buttons inside the sidebar scroll frame.
        """
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
            btn = SidebarButton(
                master=self.layout.nav_scroll_frame,
                text=name,
                icon=icon,
                command=lambda n=name: self.navigation_manager.show_page(n)
            )
            btn.grid(row=idx, column=0, sticky="ew", pady=2)
            self.navigation_manager.register_button(name, btn)

    def create_theme_selector(self) -> None:
        """
        Renders visual visual mode selector menu in the sidebar footer container.
        """
        theme_label = ctk.CTkLabel(
            self.layout.sidebar_footer, 
            text="Visual Mode", 
            font=ThemeManager.get_font(size=11), 
            text_color=ThemeManager.get_color("text_muted")
        )
        theme_label.pack(anchor="w", pady=(0, ThemeManager.PAD_XS))
        
        theme_menu = ctk.CTkOptionMenu(
            self.layout.sidebar_footer,
            values=["Dark", "Light"],
            font=ThemeManager.get_font(size=12),
            dropdown_font=ThemeManager.get_font(size=12),
            fg_color=ThemeManager.get_color("bg_active"),
            button_color=ThemeManager.get_color("bg_active"),
            button_hover_color=ThemeManager.get_color("bg_card"),
            dropdown_fg_color=ThemeManager.get_color("bg_card"),
            dropdown_hover_color=ThemeManager.get_color("bg_active"),
            dropdown_text_color=ThemeManager.get_color("text_primary"),
            text_color=ThemeManager.get_color("text_primary"),
            corner_radius=ThemeManager.CORNER_RADIUS_SM,
            command=self.change_theme_mode
        )
        theme_menu.pack(fill="x")

    def initialize_status_metrics(self) -> None:
        """
        Seeds baseline database and camera metrics in the status bar at launch.
        """
        # Determine database type and status
        db_type = "SQLite" if "sqlite" in self.settings.database_url else "Database"
        self.status_manager.update_database_status(True, db_type)
        
        # Determine camera configuration state
        cam_status = f"Stream ({self.settings.camera_fps_target} FPS)" if self.settings.camera_rtsp_url else f"Local {self.settings.camera_id}"
        self.status_manager.update_camera_status(cam_status, "accent_success")
        
        # Set default state of face recognition engine
        self.status_manager.update_recognition_engine("Biometrics Idle", "text_muted")

    def change_theme_mode(self, val: str) -> None:
        """
        Handles visuals toggling and delegates runtime redrawing parameters.
        """
        ThemeManager.set_appearance_mode(val.lower())
