# ==============================================================================
# Face Recognition Attendance System - Authentication & Setup Views
# ==============================================================================

import customtkinter as ctk
from src.gui.themes import ThemeManager
from src.controllers.auth_controller import AuthController

class LoginPage(ctk.CTkFrame):
    """
    Implements GUI for authentication checks. Displays first-run administrative
    onboarding if no accounts are present in database, else renders standard login form.
    """
    def __init__(self, parent, on_login_success_callback) -> None:
        super().__init__(parent, fg_color=ThemeManager.get_color("bg_main"))
        self.on_success = on_login_success_callback
        self.controller = AuthController()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Determine active view state
        self.is_first_run = not self.controller.system_has_users()
        
        # Render interface
        self.create_auth_panel()

    def create_auth_panel(self) -> None:
        """
        Builds the central login/setup card.
        """
        # Outer alignment container
        card = ctk.CTkFrame(
            self,
            fg_color=ThemeManager.get_color("bg_card"),
            border_color=ThemeManager.get_color("border"),
            border_width=ThemeManager.BORDER_WIDTH,
            corner_radius=ThemeManager.CORNER_RADIUS_LG,
            width=420,
            height=460
        )
        card.grid(row=0, column=0, padx=20, pady=20)
        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)
        
        # 1. Branding Header
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(fill="x", padx=ThemeManager.PAD_XL, pady=(40, 20))
        
        logo = ctk.CTkLabel(header_frame, text="🛡️", font=ThemeManager.get_font(size=40))
        logo.pack(pady=(0, 10))
        
        title_text = "System Setup Wizard" if self.is_first_run else "Security Account Login"
        self.title_lbl = ctk.CTkLabel(
            header_frame, 
            text=title_text, 
            font=ThemeManager.get_font(size=18, weight="bold"),
            text_color=ThemeManager.get_color("text_primary")
        )
        self.title_lbl.pack()
        
        desc_text = "Register the initial administrator account to configure system parameters." if self.is_first_run else "Enter your administrator credentials to access features."
        self.desc_lbl = ctk.CTkLabel(
            header_frame, 
            text=desc_text, 
            font=ThemeManager.get_font(size=11),
            text_color=ThemeManager.get_color("text_muted"),
            wraplength=340,
            justify="center"
        )
        self.desc_lbl.pack(pady=(5, 0))
        
        # 2. Form Inputs
        self.form_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.form_frame.pack(fill="x", padx=ThemeManager.PAD_XL, pady=10)
        
        # Username Entry
        lbl_user = ctk.CTkLabel(self.form_frame, text="Username", font=ThemeManager.get_font(size=11, weight="bold"), text_color=ThemeManager.get_color("text_light"))
        lbl_user.pack(anchor="w", pady=(0, 2))
        self.user_entry = ctk.CTkEntry(
            self.form_frame, 
            placeholder_text="e.g. admin_name", 
            font=ThemeManager.get_font(size=12),
            height=32
        )
        self.user_entry.pack(fill="x", pady=(0, 12))
        self.user_entry.bind("<Return>", lambda e: self.trigger_submit())
        
        # Password Entry
        lbl_pass = ctk.CTkLabel(self.form_frame, text="Password", font=ThemeManager.get_font(size=11, weight="bold"), text_color=ThemeManager.get_color("text_light"))
        lbl_pass.pack(anchor="w", pady=(0, 2))
        self.pass_entry = ctk.CTkEntry(
            self.form_frame, 
            placeholder_text="••••••••", 
            show="•",
            font=ThemeManager.get_font(size=12),
            height=32
        )
        self.pass_entry.pack(fill="x", pady=(0, 12))
        self.pass_entry.bind("<Return>", lambda e: self.trigger_submit())
        
        # Confirm Password (only on first run setup)
        if self.is_first_run:
            lbl_confirm = ctk.CTkLabel(self.form_frame, text="Confirm Password", font=ThemeManager.get_font(size=11, weight="bold"), text_color=ThemeManager.get_color("text_light"))
            lbl_confirm.pack(anchor="w", pady=(0, 2))
            self.confirm_entry = ctk.CTkEntry(
                self.form_frame, 
                placeholder_text="••••••••", 
                show="•",
                font=ThemeManager.get_font(size=12),
                height=32
            )
            self.confirm_entry.pack(fill="x", pady=(0, 12))
            self.confirm_entry.bind("<Return>", lambda e: self.trigger_submit())
            
        # 3. Status Error Label
        self.error_lbl = ctk.CTkLabel(
            card,
            text="",
            font=ThemeManager.get_font(size=11, weight="bold"),
            text_color=ThemeManager.get_color("accent_danger"),
            wraplength=340
        )
        self.error_lbl.pack(pady=2)
        
        # 4. Action Submit Button
        btn_text = "Register Admin Account" if self.is_first_run else "Authenticate Login"
        self.submit_btn = ctk.CTkButton(
            card,
            text=btn_text,
            font=ThemeManager.get_font(size=12, weight="bold"),
            fg_color=ThemeManager.get_color("accent_primary"),
            text_color=ThemeManager.get_color("text_dark"),
            hover_color=ThemeManager.get_color("bg_active"),
            height=36,
            command=self.trigger_submit
        )
        self.submit_btn.pack(fill="x", padx=ThemeManager.PAD_XL, pady=(10, 20))

    def trigger_submit(self) -> None:
        """
        Validates the entries and submits credentials to register or login.
        """
        self.error_lbl.configure(text="")
        username = self.user_entry.get().strip()
        password = self.pass_entry.get()
        
        if not username or not password:
            self.error_lbl.configure(text="Username and password fields cannot be empty.")
            return
            
        if self.is_first_run:
            confirm = self.confirm_entry.get()
            if password != confirm:
                self.error_lbl.configure(text="Passwords do not match.")
                return
            if len(password) < 6:
                self.error_lbl.configure(text="Password must contain at least 6 characters.")
                return
                
            # Perform first run admin creation
            user = self.controller.register_first_admin(username, password)
            if user:
                # Transition to login page
                self.is_first_run = False
                
                # Redraw auth card as login form
                for child in self.winfo_children():
                    child.destroy()
                self.create_auth_panel()
                self.error_lbl.configure(
                    text="Administrator registered successfully. Please log in.",
                    text_color=ThemeManager.get_color("accent_success")
                )
            else:
                self.error_lbl.configure(text="Failed to register administrator.")
        else:
            # Authenticate Login
            user = self.controller.login(username, password)
            if user:
                logger = AuthController().auth_service.logger
                logger.info(f"Successful GUI login for user: '{username}'")
                self.on_success(user)
            else:
                self.error_lbl.configure(
                    text="Invalid username or password credentials.",
                    text_color=ThemeManager.get_color("accent_danger")
                )
