# UI Dashboard View Design Specification

This document details the layout structure, operational telemetry fields, and console logger panels implemented within the main dashboard page view.

---

## 1. Grid Grid Layout Structure

The Dashboard page is structured using a 3x3 layout inside the main `content_frame`:

```
+-------------------------------------------------------------------------------+
|                               System Dashboard                                |
|  Operational metrics overview and biometric engine status diagnostics.         |
+-------------------------------------------------------------------------------+
|   [ Metric Card 1 ]       |       [ Metric Card 2 ]     |   [ Metric Card 3 ]  |
|  Total Students: 154      |       Active Faculty: 18    |   Attendance: 92.2%  |
+---------------------------+-----------------------------+----------------------+
|                     [ Core Settings Panel ]             | [ Biometrics Panel ] |
|  - Env Mode: development                                | - Engine: Offline    |
|  - DB Location: sqlite:///database/app_database.db       | - Dataset: 154 Temps |
+---------------------------------------------------------+----------------------+
|                           [ Activity Console Logs ]                           |
|  2026-08-04 21:35:37 [INFO] app.bootstrap: Initializing workspace...         |
+-------------------------------------------------------------------------------+
```

---

## 2. Component Specifications

### 2.1 KPI Metric Cards (Row 0)
Designed to represent high-priority operations statistics using `StatisticWidget` components:
1. **Total Enrolled Students**: Highlights secondary violet palette (`accent_secondary`).
2. **Active Faculty Members**: Highlights primary purple palette (`accent_primary`).
3. **Today's Attendance**: Highlights success green palette (`accent_success`). Presents total check-ins against enrolled rosters.

### 2.2 System Settings Panel (Row 1, Columns 0-1)
Renders configuration metrics fetched from system `.env` variables:
- **Environment Mode**: Configured app execution context.
- **Database Location**: SQLite driver connection URI.
- **Log Level Priority**: Roll priority.
- **Model Directory Path**: Absolute path mappings for ONNX files.

### 2.3 Biometric Diagnostics Panel (Row 1, Column 2)
Displays deep-learning inference loop status indicators:
- **Recognition Engine**: Active state of local webcam recognition threads.
- **Face Dataset Storage**: Number of stored embedding templates.
- **Confidence Threshold**: Math confidence cut-off limits.
- **Camera Stream Link**: Local USB device indices or RTSP camera endpoints.

### 2.4 Activity Console Logs (Row 2, Columns 0-2)
An embedded read-only multiline terminal window displaying system status statements directly from log handlers. Facilitates real-time debugging.
