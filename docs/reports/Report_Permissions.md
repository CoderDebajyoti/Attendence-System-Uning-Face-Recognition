# Report Permissions & Access Control

This document describes authorization boundaries for reporting metrics.

## Role Permissions
The system coordinates report generation visibility based on roles defined in the authentication layer:
- **`Administrator`**: Full unrestricted access. Can run reports globally for all departments, courses, and students, and perform manual status corrections/deletions.
- **`Faculty`**: Restricted department level access. Can run reports only for students enrolled within their designated academic department. Manual changes require override logs.
- **`Student` / `Viewer`**: Cannot access the Reports tab. Can only view their personal statistics card inside their profile detail window.
