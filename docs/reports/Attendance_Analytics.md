# Attendance Analytics

This document details statistics collection and calculations.

## Summary Analytics API
The `AttendanceAnalyticsService` returns structured JSON/dict payloads containing:
- **`total_records`**: Total marked rows.
- **`present`**: Standard check-ins.
- **`late`**: Late check-ins.
- **`absent`**: Absences recorded.
- **`excused`**: Excused absences.
- **`rate`**: Overall percentage.

## Trends Tracking
The trends feature aggregates date-wise check-ins over a configurable period (default 7 days):
```json
[
  {"date": "2026-08-10", "day_name": "Monday", "rate": 91.2},
  {"date": "2026-08-11", "day_name": "Tuesday", "rate": 88.5}
]
```
These trends populate the Dashboard graphs and report visualizers.
