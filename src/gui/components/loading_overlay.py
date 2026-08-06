# ==============================================================================
# Face Recognition Attendance System - Reusable Loading Overlay
# ==============================================================================

import customtkinter as ctk
from src.gui.themes import ThemeManager

class LoadingOverlay(ctk.CTkFrame):
    """
    A fullscreen or frame-bounded modal overlay that blocks mouse clicks 
    and displays an active progress bar with status updates during tasks.
    """
    def __init__(self, master, message: str = "Processing request..."):
        super().__init__(
            master=master,
            fg_color=ThemeManager.get_color("bg_main"),
            corner_radius=0
        )
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Centered visual frame
        panel = ctk.CTkFrame(self, fg_color="transparent")
        panel.grid(row=0, column=0)
        
        # Progress Bar / Indeterminate loader
        self.progress = ctk.CTkProgressBar(
            panel,
            width=200,
            mode="indeterminate",
            progress_color=ThemeManager.get_color("accent_primary"),
            fg_color=ThemeManager.get_color("bg_active")
        )
        self.progress.pack(pady=ThemeManager.PAD_MD)
        self.progress.start()
        
        # Loading Message
        self.label = ctk.CTkLabel(
            panel,
            text=message,
            font=ThemeManager.get_font(size=14, weight="bold"),
            text_color=ThemeManager.get_color("text_primary")
        )
        self.label.pack(pady=ThemeManager.PAD_XS)

    def update_message(self, message: str) -> None:
        """
        Dynamically updates the displayed loading message.
        """
        self.label.configure(text=message)

    def show(self) -> None:
        """
        Displays overlay in parent frame, locking down interactive operations.
        """
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.tkraise()
        self.progress.start()

    def hide(self) -> None:
        """
        Removes the overlay blocks and stops active animators.
        """
        self.progress.stop()
        self.place_forget()
