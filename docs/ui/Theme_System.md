# Theme Manager & Style Tokens Specification

This document details color palettes, typography mappings, and spacing tokens defined within the centralized `ThemeManager` system.

---

## 1. Palette Architecture

The application defines custom color maps for both Dark and Light visual modes, utilizing curated HSL palettes:

### 1.1 Dark Mode (Catppuccin Mocha-inspired Slate)
- **BG Canvas**: `#1e1e2e` (sleek dark slate main window canvas)
- **BG Sidebar**: `#11111b` (deeper dark panel contrast)
- **BG Card**: `#252538` (soft slate grey card boxes)
- **Accent Primary**: `#cba6f7` (royal violet accent focus)
- **Accent Success**: `#a6e3a1` (emerald green check-in tags)
- **Accent Danger**: `#f38ba8` (pastel red warning indicator)

### 1.2 Light Mode (Clean Slate & Violet)
- **BG Canvas**: `#f2f2f7` (soft iOS-like background grey)
- **BG Sidebar**: `#ffffff` (pure white panel highlights)
- **BG Card**: `#e5e5ea` (cool grey border blocks)
- **Accent Primary**: `#8e2de2` (deep violet brand highlight)
- **Accent Success**: `#34c759` (iOS green check-in tags)
- **Accent Danger**: `#ff3b30` (high contrast alert red)

---

## 2. Layout Tokens

Consistency is maintained across pages using fixed scale constraints:

### 2.1 Spacing Scales
- **XS**: `4px` (label padding)
- **SM**: `8px` (button margins)
- **MD**: `12px` (sub-panel alignments)
- **LG**: `16px` (card padding)
- **XL**: `24px` (header borders)

### 2.2 Rounded Corners (Radius)
- **Small (SM)**: `6px` (buttons, badges)
- **Medium (MD)**: `10px` (standard settings cards, inputs)
- **Large (LG)**: `16px` (main dashboard layout panels)

---

## 3. Typography Scale (Segoe UI)

Standardized typeface configurations:

- **Large Page Title**: Size `24`, Bold
- **Panel Header**: Size `14`, Bold
- **Standard Button/Label**: Size `13`, Normal
- **Small Status/Badge**: Size `10`, Bold/Muted
- **Monospace Code Logs**: Size `11`, Monospace (`Consolas`)
