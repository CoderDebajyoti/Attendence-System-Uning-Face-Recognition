# Attendance Rate Metrics Calculation

This document outlines the formulas and definition of opportunities used throughout the system.

## Central Metric Source
All calculations are computed solely by `AttendanceAnalyticsService` to ensure consistency.

## Mathematical Formula
The attendance rate is defined as:
$$\text{Attendance Rate} = \frac{\text{Present Count} + \text{Late Count}}{\text{Total Opportunities}} \times 100$$

### Defining "Total Opportunities"
- **Individual Student (Date Range)**:
  Opportunities are calculated as the count of distinct active session dates matching the range in the database:
  $$\text{Opportunities} = \text{Count of unique active session dates}$$
- **Institutional / Course Level (Date Range)**:
  $$\text{Opportunities} = \text{Total Active Enrolled Students} \times \text{Distinct Sessions Count}$$

### Absence Rules
- If no attendance row exists for a student on a given session date, they are not treated as "Absent" unless an explicit absence record was generated. This prevents misleading statistics during mid-semester reporting.
