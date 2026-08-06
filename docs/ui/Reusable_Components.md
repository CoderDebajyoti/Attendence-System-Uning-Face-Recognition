# UI Component Library Specification

This document details the layout specifications, parameters, and APIs of the reusable components.

---

## 1. Primary Components Registry

### 1.1 Sidebar Button (`SidebarButton`)
- **Base Class**: `customtkinter.CTkButton`
- **Purpose**: Styled navigation links mapping icons, raw text, and toggle focus states.
- **Properties**:
  - `set_active(active: bool)`: Toggles active status styles (focus background, violet text, bold typography).

### 1.2 Card Widget (`Card`)
- **Base Class**: `customtkinter.CTkFrame`
- **Purpose**: Basic modular layout container panel using token corner rounding and border styling rules.
- **Constructor Parameters**:
  - `fg_color` (optional): Backing color override.
  - `border_color` (optional): Border stroke color override.
  - `border_width` (optional): Border stroke size limit.
  - `corner_radius` (optional): Corner rounding limit.

### 1.3 Statistic Widget (`StatisticWidget`)
- **Base Class**: `Card`
- **Purpose**: High-visibility dashboard telemetry metrics blocks. Displays an icon, bold number label, subtitle, and an accent bar.
- **Constructor Parameters**:
  - `title`: Telemetry category tag.
  - `value`: Numerical measurement string.
  - `icon`: Emojis or image symbols.
  - `accent_color`: Color of the top visual highlight bar.
- **API**:
  - `update_value(new_value: str)`: Dynamic text updates.

### 1.4 Modal Dialog Box (`Dialog`)
- **Base Class**: `customtkinter.CTkToplevel`
- **Purpose**: Centered blocking dialog overlay. Prevents input events from targeting parent containers until resolved.
- **Constructor Parameters**:
  - `parent`: Parent window reference.
  - `title`: OS title window tag.
  - `width` / `height`: Window geometry dimensions.

### 1.5 Message Alert Box (`MessageBox`)
- **Base Class**: `Dialog`
- **Purpose**: Prompts, confirmation questions, or warning alerts.
- **Constructor Parameters**:
  - `icon_type`: `"info"`, `"success"`, `"warning"`, `"error"`. Sets matching emoji and status accent colors.
  - `show_cancel`: If `True`, renders a secondary cancellation button.
- **API**:
  - Query `self.result` to check user choice (`True` for Confirm, `False` for Cancel).

### 1.6 Loading Overlay (`LoadingOverlay`)
- **Base Class**: `customtkinter.CTkFrame`
- **Purpose**: Transparent blocking pane presenting status feedback during asynchronous work.
- **API**:
  - `show()`: Mounts overlay into viewport.
  - `hide()`: Unmounts overlay and releases event loop lock.
  - `update_message(msg: str)`: Dynamically changes progress description.
