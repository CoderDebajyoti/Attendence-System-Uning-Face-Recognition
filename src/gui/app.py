# ==============================================================================
# Face Recognition Attendance System - Main Application Shell Coordinator
# ==============================================================================

import customtkinter as ctk
import logging
from src.gui.themes import ThemeManager
from src.gui.window_manager import WindowManager
from src.gui.layouts import MainLayout
from src.gui.pages import (
    PageManager, DashboardPage, StudentsPage, DatasetPage,
    RecognitionPage, AttendancePage, ReportsPage, SettingsPage, AboutPage, LoginPage
)
from src.gui.navigation import NavigationManager
from src.gui.status_manager import StatusManager
from src.gui.components import SidebarButton

logger = logging.getLogger("app.gui")

class AppShell(ctk.CTk):
    """
    Main application shell window coordinator. Handles login check transitions
    and lazily loads MainLayout view ports upon user verification.
    """
    def __init__(self, settings) -> None:
        super().__init__()
        self.settings = settings
        self.current_user = None
        
        # 1. Initialize Window geometry, constraints, and centering
        WindowManager.initialize_window(self, "Face Recognition Attendance System")
        
        # 2. Setup appearance mode based on settings
        ThemeManager.set_appearance_mode("dark")
        
        # 3. Present authentication screen first
        self.show_login_screen()

    def show_login_screen(self) -> None:
        """
        Clears the workspace and draws the login interface.
        """
        # Clear child widgets
        for child in self.winfo_children():
            child.destroy()
            
        self.current_user = None
        
        # Set up login screen frame
        self.login_page = LoginPage(self, self.on_login_success)
        self.login_page.pack(fill="both", expand=True)

    def on_login_success(self, user) -> None:
        """
        Callback triggered by LoginPage upon successful verification.
        Loads the main layout workspace context.
        """
        self.current_user = user
        
        # Clear the login view
        for child in self.winfo_children():
            child.destroy()
            
        # Re-configure main grid sizing weights
        self.grid_columnconfigure(0, weight=0) # Sidebar column
        self.grid_columnconfigure(1, weight=1) # Content container
        self.grid_rowconfigure(0, weight=1)

        # 1. Initialize Main Layout Manager
        self.layout = MainLayout(self)
        
        # 2. Instantiate Page Manager
        self.page_manager = PageManager(self.layout.page_container, self)
        
        # 3. Register application pages
        self.register_application_pages()
        
        # 4. Instantiate Status Bar Manager and seed variables
        self.status_manager = StatusManager(self.layout.status_bar)
        self.initialize_status_metrics()
        self.status_manager.update_user(user.username)
        
        # 5. Instantiate Navigation Manager
        self.navigation_manager = NavigationManager(
            layout=self.layout, 
            page_manager=self.page_manager, 
            header_label=self.layout.breadcrumb_label
        )
        
        # 6. Render and hook up sidebar menu items
        self.create_navigation_menu()
        self.create_theme_selector()
        
        # 7. Load dashboard view initially
        self.navigation_manager.show_page("Dashboard")
        logger.info(f"Main workspace view successfully loaded for user '{user.username}'.")

    def logout(self) -> None:
        """
        Resets user sessions and triggers redirection back to login page view.
        """
        logger.info(f"User '{self.current_user.username}' logged out.")
        
        # Clean current grid configurations
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)
        
        self.show_login_screen()

    def register_application_pages(self) -> None:
        """
        Registers lazy-instantiated pages with the Page Manager registry.
        """
        pages_registry = {
            "Dashboard": DashboardPage,
            "Students": StudentsPage,
            "Dataset": DatasetPage,
            "Recognition": RecognitionPage,
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
            ("Dataset", "📂"),
            ("Recognition", "👤"),
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

        # Add Logout button
        logout_btn = ctk.CTkButton(
            self.layout.sidebar_footer,
            text="🚪 Logout",
            font=ThemeManager.get_font(size=12, weight="bold"),
            fg_color=ThemeManager.get_color("bg_active"),
            text_color=ThemeManager.get_color("accent_danger"),
            hover_color=ThemeManager.get_color("bg_card"),
            height=32,
            command=self.logout
        )
        logout_btn.pack(fill="x", pady=(ThemeManager.PAD_MD, 0))

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
        
        # Determine face recognition engine status
        try:
            from src.services.face_recognition_service import FaceRecognitionService
            rec_service = FaceRecognitionService.get_instance(self.settings)
            status = rec_service.get_model_status()
            status_colors = {
                "READY": "accent_success",
                "OUTDATED": "accent_warning",
                "BUILDING": "accent_warning",
                "INVALID": "accent_danger",
                "NOT_BUILT": "text_muted"
            }
            status_text = f"Model: {status.replace('_', ' ')}"
            self.status_manager.update_recognition_engine(status_text, status_colors.get(status, "text_muted"))
        except Exception:
            self.status_manager.update_recognition_engine("Biometrics Idle", "text_muted")

    def change_theme_mode(self, val: str) -> None:
        """
        Handles visuals toggling and delegates runtime redrawing parameters.
        """
        ThemeManager.set_appearance_mode(val.lower())
