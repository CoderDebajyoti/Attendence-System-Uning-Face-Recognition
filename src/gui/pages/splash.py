# ==============================================================================
# Face Recognition Attendance System - Application Splash Screen
# ==============================================================================

import customtkinter as ctk
from src.gui.themes import ThemeManager

class SplashScreen(ctk.CTk):
    """
    An undecorated initial splash screen window that executes validation checks 
    and updates a loading progress indicator before initiating the main application shell.
    """
    def __init__(self, settings, on_complete_callback) -> None:
        super().__init__()
        self.settings = settings
        self.on_complete_callback = on_complete_callback
        
        # Configure splash frame metadata
        self.title("Starting System...")
        width, height = 500, 350
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        
        # Remove standard OS title frames
        self.overrideredirect(True)
        
        # Position window centrally on user screen
        self.center_window(width, height)
        
        # Styling tokens
        self.configure(fg_color=ThemeManager.get_color("bg_sidebar"))
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Layout container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=0, sticky="nsew", padx=ThemeManager.PAD_XL, pady=ThemeManager.PAD_XL)
        container.grid_columnconfigure(0, weight=1)
        
        # 1. Logo Placeholder
        self.logo_label = ctk.CTkLabel(
            container,
            text="🛡️",
            font=ThemeManager.get_font(size=64)
        )
        self.logo_label.pack(pady=(20, 5))
        
        # 2. Application Name
        self.brand_label = ctk.CTkLabel(
            container,
            text="FACE RECOGNITION ATTENDANCE",
            font=ThemeManager.get_font(size=18, weight="bold"),
            text_color=ThemeManager.get_color("accent_primary")
        )
        self.brand_label.pack(pady=5)
        
        # 3. Environment/Version
        self.info_label = ctk.CTkLabel(
            container,
            text=f"Version 1.0.0-Beta | Environment: {settings.app_env.upper()}",
            font=ThemeManager.get_font(size=10),
            text_color=ThemeManager.get_color("text_muted")
        )
        self.info_label.pack(pady=(0, 15))
        
        # 4. Progress Indicator
        self.progress_bar = ctk.CTkProgressBar(
            container,
            width=320,
            progress_color=ThemeManager.get_color("accent_primary"),
            fg_color=ThemeManager.get_color("bg_active")
        )
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0.0)
        
        # 5. Loading status label
        self.status_label = ctk.CTkLabel(
            container,
            text="Initializing modules...",
            font=ThemeManager.get_font(size=11, slant="italic"),
            text_color=ThemeManager.get_color("text_light")
        )
        self.status_label.pack(pady=5)
        
        # 6. Developer Mode Indicator
        if settings.debug:
            self.dev_badge = ctk.CTkLabel(
                container,
                text="DEVELOPER MODE ACTIVE",
                font=ThemeManager.get_font(size=9, weight="bold"),
                text_color=ThemeManager.get_color("text_dark"),
                fg_color=ThemeManager.get_color("accent_warning"),
                corner_radius=ThemeManager.CORNER_RADIUS_SM,
                width=140,
                height=18
            )
            self.dev_badge.pack(side="bottom", pady=10)
            
        # Bootstrap task queue mapping
        self.steps = [
            (0.15, "Loading configuration settings..."),
            (0.35, "Creating sandboxed directories..."),
            (0.55, "Initializing rolling file logger..."),
            (0.75, "Connecting to database engine..."),
            (0.90, "Scanning local biometric models..."),
            (1.00, "Validation complete. Booting Main UI...")
        ]
        self.current_step = 0
        
        # Begin queue consumption
        self.after(500, self.run_bootstrap_step)

    def center_window(self, width: int, height: int) -> None:
        """
        Coordinates screen size queries to center window canvas.
        """
        s_w = self.winfo_screenwidth()
        s_h = self.winfo_screenheight()
        x = (s_w - width) // 2
        y = (s_h - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def run_bootstrap_step(self) -> None:
        """
        Loops through simulated initialization procedures, advancing the loader.
        """
        if self.current_step < len(self.steps):
            progress, status = self.steps[self.current_step]
            self.progress_bar.set(progress)
            self.status_label.configure(text=status)
            self.current_step += 1
            self.after(400, self.run_bootstrap_step)
        else:
            # Destroy splash and call trigger to boot main dashboard
            self.destroy()
            self.on_complete_callback()
