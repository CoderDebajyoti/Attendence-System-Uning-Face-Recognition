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
from src.gui import AppShell


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

def validate_system_startup(settings) -> bool:
    """
    Validates essential system configurations and directory permissions on boot.
    """
    logger = logging.getLogger("app.bootstrap")
    logger.info("Executing system startup diagnostics...")
    
    # Check directory access
    for path_str in [settings.model_path, settings.dataset_path, settings.export_path, settings.backup_path]:
        path = Path(path_str)
        if not path.exists():
            logger.error(f"Startup check failed: Directory '{path_str}' does not exist.")
            return False
            
    # Check database URL configuration
    if not settings.database_url:
        logger.error("Startup check failed: Database connection string is empty.")
        return False
        
    logger.info("Startup diagnostics passed successfully.")
    return True

def main() -> None:
    """
    Bootstrap process loading configuration settings and launching the main Application Shell.
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
    
    # 4. Perform startup validation
    if not validate_system_startup(settings):
        logger.critical("System diagnostics failed. Aborting startup.")
        sys.exit(1)
        
    # 5. Bootstraps the main CustomTkinter Application Shell
    logger.info("Bootstrapping Application Shell GUI...")
    app = AppShell()
    
    logger.info("Application Shell ready. Launching main event loop...")
    app.mainloop()

if __name__ == "__main__":
    main()
