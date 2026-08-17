# Report Generation Pipeline

This document describes how report data is generated.

## Flow of Operations

```mermaid
sequenceDiagram
    participant GUI as ReportsPage
    participant Ctrl as ReportsController
    participant Service as AttendanceReportService
    participant Analytics as AttendanceAnalyticsService
    participant Repo as AttendanceRepository

    GUI->>Ctrl: Trigger Generate (filters)
    Ctrl->>Service: Get Report Data
    Service->>Service: Validate Date Range
    Service->>Repo: Query filtered records
    Repo-->>Service: List[Attendance]
    Service->>Analytics: Aggregate stats (dates range)
    Analytics-->>Service: Stats Dict
    Service-->>Ctrl: Compiled Report payload
    Ctrl-->>GUI: Render Preview & Summary cards
```

## Preview Panel Limits
To prevent UI lockups:
- The Reports page render preview is capped at 100 rows.
- If the dataset has $>100$ records, a footer label indicates: `"Showing first 100 rows out of N. Export report to view all entries."`
