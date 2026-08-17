# Attendance History Registry

This document outlines the visual layout and data retrieval policies for attendance history tracking.

## Registry Table Page
The master tracking panel is integrated directly into the `Attendance` tab:
- **Pagination & Limit**: To avoid locking the GUI main thread, the visual table loads and renders up to a limit of 100 matching rows.
- **Table Structure**:
  `Attendance ID | Student ID | Student Name | Time | Status | Match Score | Source`

## Student Profile History Card
A personal attendance history report is embedded under the **Students Details** card:
- Displays total sessions held, present count, late count, and individual rate.
- Lists a scrollable summary table of the 5 most recent check-in events.
