# Mermaid Architecture & Flow Diagrams

This document contains visual block diagrams, interaction sequences, and class relations for the UI framework.

---

## 1. Class Relationships & Management Composition

This diagram illustrates how `AppShell` acts as the primary coordinator, composing decoupled managers and components:

```mermaid
classDiagram
    class AppShell {
        +settings: AppSettings
        +layout: MainLayout
        +page_manager: PageManager
        +status_manager: StatusManager
        +navigation_manager: NavigationManager
        +register_application_pages()
        +create_navigation_menu()
    }

    class MainLayout {
        +sidebar: CTkFrame
        +header: CTkFrame
        +page_container: CTkFrame
        +status_bar: CTkFrame
        +create_sidebar()
        +create_main_container()
    }

    class PageManager {
        +container: CTkFrame
        +pages: dict
        +page_classes: dict
        +register_page(name, page_class)
        +raise_page(name)
    }

    class NavigationManager {
        +layout: MainLayout
        +page_manager: PageManager
        +breadcrumb_label: CTkLabel
        +buttons: dict
        +register_button(name, button)
        +show_page(name)
    }

    class StatusManager {
        +frame: CTkFrame
        +db_label: CTkLabel
        +camera_label: CTkLabel
        +time_label: CTkLabel
        +update_database_status(connected, details)
        +update_camera_status(status, color)
        +update_time()
    }

    class ThemeManager {
        <<utility>>
        +PALETTE_DARK: dict
        +PALETTE_LIGHT: dict
        +set_appearance_mode(mode)
        +get_color(key)
        +get_font(size, weight)
    }

    class WindowManager {
        <<utility>>
        +initialize_window(window, title)
        +center_on_screen(window, width, height)
    }

    AppShell --> MainLayout : composes
    AppShell --> PageManager : composes
    AppShell --> StatusManager : composes
    AppShell --> NavigationManager : composes
    
    NavigationManager --> PageManager : queries
    NavigationManager --> MainLayout : controls
    
    MainLayout ..> ThemeManager : references colors
    PageManager ..> ThemeManager : references colors
    StatusManager ..> ThemeManager : references colors
    AppShell ..> WindowManager : configures scaling
```

---

## 2. Bootstrapping & Transition Sequence

This diagram shows the sequence of checks and GUI initialization steps on startup:

```mermaid
sequenceDiagram
    autonumber
    actor User as User Execution
    participant main as main.py
    participant config as ConfigLoader
    participant diag as startup_diagnostics
    participant splash as SplashScreen
    participant app as AppShell
    participant page_mgr as PageManager

    User->>main: Execute python src/main.py
    main->>config: ConfigLoader.load_config()
    config-->>main: Return AppSettings
    main->>main: setup_directories() & initialize_logger()
    main->>diag: validate_system_startup()
    diag-->>main: Return diagnostic success
    main->>splash: Instantiate SplashScreen(settings)
    splash->>splash: overrideredirect(True) (Make Undecorated)
    splash->>splash: center_window() & run progress loop
    Note over splash: Simulates DB connect & model path maps
    splash-->>main: On loading completion, destroy splash
    main->>app: Instantiate AppShell(settings)
    app->>app: initialize_window() (Centers Main UI)
    app->>page_mgr: Register page classes (lazy mapping)
    app->>app: show_page("Dashboard")
    app-->>User: Present main dashboard window
```
