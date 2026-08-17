# Report Generation Performance

This document describes how report generation is optimized for large databases.

## SQL Query Optimization
- Filters are applied directly at the database engine level via SQLAlchemy `.filter()` calls. The system never loads the entire database into Python memory to apply filters.
- **Indexes**: Added database-level indexes to `student_id`, `session_id`, `date`, and `status` in the `attendance` table, ensuring sub-millisecond retrieval times.

## GUI Rendering Protection
- Rendering thousands of UI widgets in a CustomTkinter scroll frame would cause severe lag and freeze the event loop.
- To prevent this, the GUI preview limit is set to **100 rows**.
- Heavy file writes (CSV / Excel) write directly to disk, keeping the GUI thread responsive.
