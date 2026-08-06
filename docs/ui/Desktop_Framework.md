# Desktop GUI Framework Design Spec

This document details the modular framework designed to decouple UI operations and prevent monolithic god-classes in our CustomTkinter desktop environment.

---

## 1. Decoupled Manager Components

To keep code maintainable, testable, and compliant with SOLID design principles, responsibilities are split into six distinct managers:

### 1.1 Window Manager (`src/gui/window_manager/`)
- **Responsibility**: Screen coordinate conversions, sizing constraints, min/max dimensions limits, and initial startup placement.
- **Architectural Value**: Eliminates hardcoded screen placements. Automatically queries current monitor details to center top-level frames and popup dialog boxes.

### 1.2 Layout Manager (`src/gui/layouts/`)
- **Responsibility**: Structural grid configuration. Partitions the window into:
  - Header panel
  - Navigation sidebar
  - Page viewport container
  - Status diagnostics ribbon
- **Architectural Value**: Isolates resizing behavior rules so grid changes don't affect page content logic.

### 1.3 Theme Manager (`src/gui/themes/`)
- **Responsibility**: Color palette lookup, typography weights, font objects creation, and runtime light/dark visual mode switches.
- **Architectural Value**: Enforces consistency across all widgets. Prevents color hardcoding inside page view code.

### 1.4 Page Manager (`src/gui/pages/page_manager.py`)
- **Responsibility**: Registering, lazily instantiating, and caching views.
- **Architectural Value**: Optimizes bootstrap speed. Instead of pre-rendering all pages at launch, views are instantiated only when first visited.

### 1.5 Navigation Manager (`src/gui/navigation/`)
- **Responsibility**: Maps sidebar button click commands to corresponding page managers. Controls button focus states and updates Header breadcrumbs.
- **Architectural Value**: Completely decouples routing triggers from layout frame code.

### 1.6 Status Manager (`src/gui/status_manager/`)
- **Responsibility**: Coordinates updates to labels within the footer diagnostic ribbon (clock, user session, database status, camera fps, etc.).
- **Architectural Value**: Exposes a clean, thread-safe API for asynchronous system update indicators.
