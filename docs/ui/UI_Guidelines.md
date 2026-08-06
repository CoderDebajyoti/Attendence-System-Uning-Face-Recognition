# UI Style Guidelines & Visual Standards

This document establishes design guidelines, color maps, and alignment rules to ensure a consistent, premium UX throughout the development lifecycle.

---

## 1. Grid Alignment & Layout Consistency

- **Outer Page Padding**: Use `ThemeManager.PAD_XL` (`24px`) for outer boundaries of page containers.
- **Card Spacing**: Use `ThemeManager.PAD_SM` (`8px`) between adjacent cards in grid dashboards.
- **Grid Weights**: Always allocate expandable weights (`weight=1`) to content columns and rows to allow responsive resizing. Column `0` in main app shell must remain fixed at `230px`.

---

## 2. Color Mapping Conventions

To maintain visual hierarchy, limit color usage to functional status indicators:

- **Primary Violet Accent (`accent_primary`)**: Used for branding highlights, active navigation selection focus, and primary button indicators.
- **Secondary Blue Accent (`accent_secondary`)**: Used for numerical metrics, telemetry highlights, and informational updates.
- **Success Green (`accent_success`)**: Used exclusively to represent valid check-ins, connected statuses, and loaded databases.
- **Warning Amber (`accent_warning`)**: Used for configuration flags, developmental notices, and warning levels.
- **Danger Red (`accent_danger`)**: Used for engine errors, database connection failures, and camera offline states.

---

## 3. Typographical Hierarchy

Always use Segment/UI mappings dynamically to avoid pixelation during OS scaling:

- **Page Title**: `24pt Bold` (e.g. `System Dashboard`, `Student Registry`)
- **Card Subtitle**: `13pt Normal` (descriptive text blocks)
- **Settings Row Title**: `12pt Bold`
- **Telemetries / Numbers**: `22pt Bold` (Statistic Widget measurements)
- **Status / Clock**: `10pt Bold` (Status Bar outputs)

---

## 4. Modal Dialog Modality

To prevent layout state corruptions, modal overlays must follow these rules:

1. **Explicit Ownership**: Dialogs must pass a parent window reference (`parent`) to the constructor.
2. **Transient Hook**: `self.transient(parent)` must be invoked to keep the popup pinned above the parent frame.
3. **Event Grab**: `self.grab_set()` must be called to block interactions with background windows until resolved.
