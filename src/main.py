# ==============================================================================
# Face Recognition Attendance System - Bootstrap Entrypoint
# ==============================================================================

import logging
import sys
from pathlib import Path

# Ensure the project root directory is in the import search paths
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Auto-activate local virtual environment packages if run outside the virtual environment
venv_dir = project_root / ".venv"
if venv_dir.exists():
    # Windows fallback site-packages path
    win_site_packages = venv_dir / "Lib" / "site-packages"
    if win_site_packages.exists() and str(win_site_packages) not in sys.path:
        sys.path.insert(0, str(win_site_packages))
    
    # Unix fallback site-packages path (e.g. .venv/lib/python3.x/site-packages)
    unix_lib = venv_dir / "lib"
    if unix_lib.exists():
        for py_dir in unix_lib.glob("python3.*/site-packages"):
            if py_dir.exists() and str(py_dir) not in sys.path:
                sys.path.insert(0, str(py_dir))

import customtkinter as ctk
from src.core.config import ConfigLoader


def setup_directories(settings) -> None:
    """
    Guarantees directories existence before booting pipelines.
    """
    for path in [settings.model_path, settings.dataset_path, settings.export_path, settings.backup_path]:
        Path(path).mkdir(parents=True, exist_ok=True)

def initialize_logger(settings) -> None:
    """
    Initializes basic rolling logging channel diagnostics.
    """
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Establish system format log file
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "app_system.log", encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main() -> None:
    """
    Bootstrap process loading configuration settings and launching verification window.
    """
    # 1. Parse configuration parameters
    settings = ConfigLoader.load_config()
    
    # 2. Configure filesystem hooks
    setup_directories(settings)
    
    # 3. Configure logging streams
    initialize_logger(settings)
    
    logger = logging.getLogger("app.bootstrap")
    logger.info("Initializing Face Recognition Attendance System workspace...")
    logger.info(f"Environment: {settings.app_env} | Debug: {settings.debug}")
    logger.info(f"Database URL: {settings.database_url}")
    
    # 4. Spawns custom Tkinter window for system structure validation
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    app = ctk.CTk()
    app.title("Face Recognition Attendance System - Setup Verification")
    app.geometry("600x400")
    
    # Visual overlay labels
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
        text="GUI Panels and AI Inference loops will be integrated in subsequent phases.", 
        text_color="gray",
        font=ctk.CTkFont(size=12, slant="italic")
    )
    info_label.pack(side="bottom", pady=20)
    
    logger.info("Startup validation GUI window ready. Launching loop...")
    app.mainloop()

if __name__ == "__main__":
    main()
