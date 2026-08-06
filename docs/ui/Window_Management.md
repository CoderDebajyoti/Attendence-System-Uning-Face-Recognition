# Window Geometry, Scaling & Constraints

This document details sizing constraints, screen positioning calculations, and modal dialog constraints of the application window.

---

## 1. Primary Window Dimensions

The application enforces standard sizing constraints to ensure compatibility across screen resolutions:

- **Default Launch Size**: `1200 x 800` pixels.
- **Minimum Enforced Size**: `1024 x 768` pixels. Resizing below this limit is blocked to prevent widget compression.

---

## 2. Positioning Algorithms

### 2.1 Center-on-Screen (Main App)
To calculate coordinates for centering the primary frame, we query display boundaries:

$$X = \frac{\text{Screen Width} - \text{Window Width}}{2}$$

$$Y = \frac{\text{Screen Height} - \text{Window Height}}{2}$$

```python
s_w = window.winfo_screenwidth()
s_h = window.winfo_screenheight()
x = (s_w - width) // 2
y = (s_h - height) // 2
window.geometry(f"{width}x{height}+{x}+{y}")
```

### 2.2 Parent-Centred Dialogs (Modals)
To prevent popup dialog boxes from spawning on random screen regions, we position them relative to the main window container coordinate frame:

$$X_{dialog} = X_{parent} + \frac{\text{Parent Width} - \text{Dialog Width}}{2}$$

$$Y_{dialog} = Y_{parent} + \frac{\text{Parent Height} - \text{Dialog Height}}{2}$$

---

## 3. Responsive Scaling & Grid Weights

To maintain full responsiveness, parent layout containers use Tkinter grid configuration weights:
- **Sidebar**: Column weight `0` (fixed width `230px` to prevent text deformation).
- **Workspace Canvas**: Column weight `1` (takes up remaining horizontal resolution).
- **Page Container Grid**: Row weight `1` (takes up remaining vertical resolution).
- **Main Content Frames**: Page view widgets use relative `sticky="nsew"` gridding to stretch contents dynamically.
