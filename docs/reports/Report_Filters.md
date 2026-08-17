# Report Filters Validation

This document describes options and validation rules for report query filtering.

## Filter Fields
The Reports tab supports selecting:
- **Period**: Today, Yesterday, This Week, This Month, Custom Range.
- **Custom Range**: Start Date and End Date (`YYYY-MM-DD`).
- **Student**: Filter for a single student profile.
- **Department**: Abbreviation tags (e.g. CSE, ECE).
- **Course**: Registered courses (filtered dynamically based on the active Department selection).
- **Status**: PRESENT, LATE, ABSENT, EXCUSED.
- **Source**: FACE_RECOGNITION, MANUAL.

## Validation Logic
Prior to executing database queries:
1. **Empty Checks**: Asserts start and end dates are non-empty.
2. **Regex / Parse Match**: Confirms date inputs follow `YYYY-MM-DD` format.
3. **Boundary Check**: Asserts $\text{Start Date} \le \text{End Date}$.

If validation fails, a pop-up warning dialog notifies the user, and report generation is aborted.
