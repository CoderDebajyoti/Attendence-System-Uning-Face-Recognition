# Attendance Operational Statistics

This document details statistics calculations across the dashboard and registry cards.

## Active Calculations
All operational statistics are computed dynamically in `AttendanceRepository` and `AttendanceService` to avoid GUI thread bottlenecking:

### 1. Attendance Rate
Calculates the ratio of present/late check-ins relative to active enrolled students:
$$\text{Attendance Rate} = \frac{\text{Present Students} + \text{Late Students}}{\text{Total Active Enrolled Students}} \times 100.0$$

### 2. Not Marked Students
$$\text{Not Marked} = \text{Total Active Enrolled Students} - \text{Total Marked Today}$$

> [!NOTE]
> Students are not marked ABSENT automatically. An ABSENT status requires an explicit session cutoff trigger, preventing incorrect marking before classes conclude.

## Real-time Statistics Feeds
Stats populate:
- **Dashboard KPI Cards**: Showing Today's Attendance Rate, Present count, and Late count.
- **Attendance Page Sidebar**: Displaying a live summary count of check-ins on the current date.
