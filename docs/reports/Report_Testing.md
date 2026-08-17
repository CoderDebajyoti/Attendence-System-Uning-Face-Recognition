# Reports & Analytics Testing

This document details reports verification and unit testing.

## Test Suite
Unit tests are implemented under `tests/unit/test_reports_service.py` using `pytest`.

## Scenarios Covered
1. **Date Range Validation**: Assures start/end format parses and boundary conditions are validated.
2. **Filters Coverage**: Verifies filtering logs by range, status, department, and source.
3. **Analytics Equations**: Confirms attendance rate formulas match mathematical specifications.
4. **Student Analytics Profile**: Verifies first/last check-in dates and personal rate calculations.
5. **CSV/Excel Generation**: Simulates file export to a temporary path and asserts that the physical files are written successfully.
6. **Rejection Safeguards**: Verifies empty reports are blocked from export and return correct failure messages.
