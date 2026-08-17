# Excel Export Engine

This document details the multi-sheet Excel report generator using `openpyxl`.

## Sheet Layout
Excel reports are split into two tabs:

### Sheet 1: Attendance Records
- Contains the master logs database rows.
- **Styling**: Segoe UI fonts, bold white headers with dark blue background fill (`#2A3F54`), and centered text alignment.
- **Columns**: Identical to CSV columns.
- **Auto-fit Widths**: Calculated dynamically to prevent text truncation.

### Sheet 2: Summary Report
- Merged green title block (`#1ABB9C`).
- Key-value rows detailing Start Date, End Date, Total Records, Present, Late, Absent, Excused, Opportunities, and Overall Attendance Rate.

## Dependency Check
The engine imports `openpyxl`. If unavailable, a friendly pop-up alert warns the user.
