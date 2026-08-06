# Application Lifecycle & Interaction Workflow

This document explains the runtime sequence of actions, starting from command line execution to view rendering, routing transitions, and application exit.

---

## 1. Startup & Bootstrap Workflow

```
[ Developer runs python src/main.py ]
                  |
                  v
[ main.py imports sys search paths ]
                  |
                  v
[ ConfigLoader parses settings from .env ]
                  |
                  v
[ setup_directories creates directories ]
                  |
                  v
[ initialize_logger launches rolling logs ]
                  |
                  v
[ validate_system_startup checks paths & db url ]
                  |
                  v
[ SplashScreen initializes (undecorated window) ]
                  |
                  v
[ SplashScreen runs simulated validation progress loops ]
                  |
                  v
[ On complete, SplashScreen destroys self & fires callback ]
                  |
                  v
[ AppShell coordinates components initialization ]
                  |
                  v
[ MainLayout grids Header, Sidebar, Viewport, Status Bar ]
                  |
                  v
[ PageManager registers available pages in dictionary ]
                  |
                  v
[ NavigationManager creates menu buttons & sets Dashboard active ]
                  |
                  v
[ AppShell mainloop active (main window rendered) ]
```

---

## 2. Navigation Transition Workflow

1. **User Interaction**:
   The user clicks a navigation item (e.g. "Dataset") in the left sidebar menu.

2. **Routing Routing Request**:
   The button click triggers `navigation_manager.show_page("Dataset")`.

3. **Active Button Redraw**:
   - `NavigationManager` iterates through registered sidebar buttons.
   - Clears focus state from the previous selection.
   - Applies violet focus styling (active state) to the "Dataset" button.

4. **Page Viewport Swap**:
   - `NavigationManager` invokes `page_manager.raise_page("Dataset")`.
   - `PageManager` checks if `DatasetPage` has already been loaded in memory.
     - **If cached**: Retrieves it from the dictionary.
     - **If first request**: Instantiates `DatasetPage(parent=page_container, controller=app)`, grids it, and saves it in the cache.
   - Calls `DatasetPage.tkraise()` to bring it to the top of the grid stack.

5. **Metadata Update**:
   - The breadcrumb label in the top header is updated to `System / Dataset`.
   - Page telemetry metrics load if available.
