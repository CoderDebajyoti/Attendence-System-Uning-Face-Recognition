# Face Recognition Attendance System - Feature Planning

This document defines the release plan for the Face Recognition Attendance System, categorizing features into core milestones (v1.0), advanced functional versions (v2.0), and long-term future extensions (v3.0).

---

## 1. Feature Release Matrix

The table below lists all planned features, their tier class, complexity (Low, Medium, High), and release versions:

| Feature Name | Category | Complexity | Target Version | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Secure Authentication** | Core | Medium | v1.0 | Admin and Faculty user login with encrypted passwords. |
| **Student Directory** | Core | Low | v1.0 | Full CRUD management for student profiles. |
| **Camera Feed Capture** | Core | Medium | v1.0 | Asynchronous camera reading canvas supporting multiple local camera feeds. |
| **Dataset Capturer Wizard** | Core | High | v1.0 | enrollment wizard capturing 10 distinct facial frames with landmark alignment. |
| **Basic Matching Engine** | Core | High | v1.0 | Cosine similarity calculation comparing query inputs against database profiles. |
| **Manual Override** | Core | Low | v1.0 | UI panel permitting faculty to manually change attendance statuses. |
| **CSV/Excel Export** | Core | Low | v1.0 | Basic table dumps to CSV and Excel. |
| **System Logger** | Core | Low | v1.0 | Text-based diagnostics logs for database and hardware connection errors. |
| **Modern Dashboard** | Core | Medium | v1.0 | High-quality CustomTkinter main interface with KPI indicators. |
| **Auto Cooldown Filters** | Advanced | Medium | v2.0 | Automated timer window ignoring repeat detections of the same student within 30 minutes. |
| **Local Database Backups** | Advanced | Low | v2.0 | Automated backups of the SQLite database file on application shutdown. |
| **Liveness Check v1** | Advanced | High | v2.0 | Basic texture analysis and eye-blink detection to prevent photo-spoofing attacks. |
| **Plotly Visual Analytics** | Advanced | Medium | v2.0 | Interactive widgets showing attendance histograms and absenteeism charts. |
| **PDF Report Exporter** | Advanced | Medium | v2.0 | Styled PDF reports containing logos and structured performance grids. |
| **Email Absentee Alerts** | Enterprise | Medium | v2.0 | SMTP integration to automatically email alerts for student attendance drops. |
| **Multi-Camera Feeds** | Enterprise | High | v3.0 | Central management of multiple cameras (IP RTSP) feeding a single tracking server. |
| **PostgreSQL Integration** | Enterprise | Medium | v3.0 | Migration config shifting DB transactions from SQLite files to network PostgreSQL. |
| **Active Directory / SSO** | Enterprise | High | v3.0 | Login authentication using standard enterprise directories (LDAP/SSO). |
| **RFID / QR Integration** | Future | Medium | v3.0 | Secondary authentication methods (QR Code, RFID card swipes) for hybrid verification. |
| **Teacher & Student Portals**| Future | High | v3.0 | Web-based student and teacher portals replacing the local desktop viewer. |
| **AI Predictive Analytics** | Future | High | v3.0 | Predict dropout risk and identify long-term absent patterns using ML. |

---

## 2. Feature Details

### 2.1 Version 1.0 (Core Desktop MVP)
Focuses on providing a fully functional standalone desktop app that can register students, capture datasets, run the local facial recognition engine, log attendance, and export raw logs to CSV.
- **Biometric Standard**: Aligned $112 \times 112$ cropping with 512-d ArcFace models.
- **Data Storage**: Single-file local SQLite database with all tables configured in 3NF.
- **UI State**: Sidebar menu, main navigation controls, frame-buffer Canvas.

### 2.2 Version 2.0 (Advanced Features)
Improves operational security and adds visual business analytics.
- **Anti-Spoofing**: Eye-blink challenge ensures students are physically present.
- **Visual Dashboards**: Integrates interactive Plotly widgets inside Tkinter. Reports are generated in PDF formats using ReportLab.
- **Automation Alerts**: System sends emails when attendance rates fall below threshold values.

### 2.3 Version 3.0 (Enterprise Deployments)
Adapts the codebase to multi-site installations and web integrations.
- **Network Database Layer**: Shifts storage to PostgreSQL, allowing multiple desktop terminal clients to read and write to the same database.
- **SSO Authentication**: Secures administrative panels behind LDAP/OAuth portals.
- **Hybrid Tracking**: Enhances accuracy by combining face scans with student QR/RFID credentials.
