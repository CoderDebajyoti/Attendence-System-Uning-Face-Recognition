# UI Architecture Specification: Presentation Layer & Bootstrap Lifecycle

This document describes the high-level architecture of the presentation layer and details the start-up bootstrap sequence of the **Face Recognition Attendance System**.

---

## 1. High-Level Design Pattern

The UI is built on a modular Model-View-Controller (MVC) or Coordinator-based presentation pattern using the **CustomTkinter** framework. It separates configuration loading, startup validation, directory preparation, and core window layout creation to achieve a clean separation of concerns.

```
+-------------------------------------------------------------+
|                        src/main.py                          |
|  (Bootstrap Entrypoint: Loader, Logger, Startup Diagnostics) |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                 src/gui/pages/splash.py                     |
|           (Undecorated startup splash view)                 |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                    src/gui/app.py                           |
|      (Main Coordinator / AppShell Window Orchestrator)      |
+-------------------------------------------------------------+
                               |
       +-----------------------+-----------------------+
       |                       |                       |
       v                       v                       v
+---------------+       +---------------+       +---------------+
| WindowManager |       | MainLayout    |       | ThemeManager  |
| (Scale/Bounds)|       | (Frame Grid)  |       | (HSL Palette) |
+---------------+       +---------------+       +---------------+
       |                       |                       |
       v                       v                       v
+---------------+       +---------------+       +---------------+
| PageManager   |       | NavigationMgr |       | StatusManager |
| (Lazy Loading)|       | (Tab Routing) |       | (Live Status) |
+---------------+       +---------------+       +---------------+
```

---

## 2. Bootstrapping Steps (`src/main.py`)

1. **Import Search Path Injector**:
   Ensures that `project_root` is inserted into `sys.path`. Automatically detects and activates virtual environments (`.venv`) on Windows and Unix if execution occurs outside the terminal environment.
   
2. **Configuration Loading (`ConfigLoader`)**:
   Reads variables from the environment (`.env`) and returns a type-safe, immutable `AppSettings` data model.

3. **Directories Enforcement (`setup_directories`)**:
   Guarantees that write-path directories (`models/`, `database/datasets`, `database/exports`, `database/backups`) exist before execution.

4. **Rolling System Logger (`initialize_logger`)**:
   Spawns a rolling logging interface mapping output stdout and a diagnostic file `logs/app_system.log`.

5. **Diagnostic Verification (`validate_system_startup`)**:
   Verifies directory read/write access permissions and connection parameters before loading any heavier Tkinter modules.

6. **Splash Loading Transition**:
   Presents the `SplashScreen` view. When it completes, the `AppShell` main window is loaded.
