# Biometric Privacy & Export Safety

This document outlines privacy boundaries when exporting and compiling attendance reports.

## Biometric Data Boundary
To protect student biometric profiles, the system enforces a strict boundary:
- Reports and spreadsheet exports must **never** contain raw face images, camera frame crops, or numpy facial embedding vectors.
- Database records only contain surrogate keys (`student_id`), time indices, matching scores, and status tags.
- Model weights (`recognition_model.xml`) are strictly stored in local system files and excluded from backups and reports.

## Audit Logs Security
- Operations such as report generation or manual entries write logging entries documenting user roles and time stamps.
- Full CSV/Excel text contents are never written to standard diagnostic system logs.
