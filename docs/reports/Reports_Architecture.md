# Reports & Analytics Architecture

This document describes the architectural bounds and separation of concerns implemented in Phase 11.

## Layer boundaries
To keep the presentation code completely independent of formatting, mathematical scoring, or data persistence:

1. **User Interface Layer (`ReportsPage`)**:
   - Collects date values and selections.
   - Delegates event requests to the Controller.
   - Refreshes preview grids and summaries.
2. **Controller Layer (`ReportsController`)**:
   - Acts as a thin bridge.
   - Fetches filter listings (Students, Departments, Courses) from `StudentService`.
   - Dispatches reports/exports requests to services.
3. **Analytics Service (`AttendanceAnalyticsService`)**:
   - Holds numerical equations for calculating metrics (e.g. attendance rate).
   - Generates trends matrices and aggregates.
4. **Report Service (`AttendanceReportService`)**:
   - Validates ranges bounds.
   - Formats log fields into printable values.
   - Generates CSV/Excel files.
5. **Persistence Layer (`AttendanceRepository`)**:
   - Fetches row collections directly from database tables using SQLAlchemy.
