# CSV Export Engine

This document details the CSV report file generator.

## CSV Columns
The generated CSV files export all attributes:
`Attendance ID, Student ID, Student Name, Roll Number, Department, Course, Date, Time In, Status, Source, Recognition Score`

## Implementation Details
1. **Safety Check**: Checks that the filtered records list is non-empty. If empty, the export is blocked, and an alert dialog notifies the user.
2. **Directory Creation**: Automatically builds folders inside the configured `export_path` directory.
3. **Safe Filenames**: Formatted using the date range and a timestamp to prevent overwriting existing files:
   `attendance_report_YYYY-MM-DD_to_YYYY-MM-DD_YYYYMMDD_HHMMSS.csv`
4. **Encoding**: Saves using `utf-8` encoding.
