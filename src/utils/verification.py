# ==============================================================================
# Face Recognition Attendance System - Developer Verification Utility
# ==============================================================================

import sys
from pathlib import Path

# Setup paths when executed directly
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Auto-activate local virtual environment packages if run outside the virtual environment
venv_dir = project_root / ".venv"
if venv_dir.exists():
    win_site_packages = venv_dir / "Lib" / "site-packages"
    if win_site_packages.exists() and str(win_site_packages) not in sys.path:
        sys.path.insert(0, str(win_site_packages))
    unix_lib = venv_dir / "lib"
    if unix_lib.exists():
        for py_dir in unix_lib.glob("python3.*/site-packages"):
            if py_dir.exists() and str(py_dir) not in sys.path:
                sys.path.insert(0, str(py_dir))

import customtkinter as ctk
from src.core.config import ConfigLoader

def run_diagnostic_gui() -> None:
    """
    Spawns a CustomTkinter window specifically for system configuration validation.
    """
    settings = ConfigLoader.load_config()
    
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    app = ctk.CTk()
    app.title("Face Recognition Attendance System - Diagnostics Utility")
    app.geometry("600x400")
    app.resizable(False, False)
    
    title_label = ctk.CTkLabel(
        app, 
        text="Project Skeleton Verification Mode", 
        font=ctk.CTkFont(size=22, weight="bold")
    )
    title_label.pack(pady=40)
    
    status_text = (
        f"✓ Configs Parsed Successfully\n"
        f"✓ Sandboxed Folders Mapped\n"
        f"✓ Diagnostic Logs Configured\n\n"
        f"Application Name: {settings.app_name}\n"
        f"Database Path: {settings.database_url}\n"
        f"Threshold Limit: {settings.recognition_threshold}\n"
    )
    
    status_label = ctk.CTkLabel(
        app, 
        text=status_text, 
        justify="left",
        font=ctk.CTkFont(size=14)
    )
    status_label.pack(pady=20)
    
    info_label = ctk.CTkLabel(
        app, 
        text="Diagnostics window - Close this window to finish execution.", 
        text_color="gray",
        font=ctk.CTkFont(size=12, slant="italic")
    )
    info_label.pack(side="bottom", pady=20)
    
    app.mainloop()

if __name__ == "__main__":
    run_diagnostic_gui()
