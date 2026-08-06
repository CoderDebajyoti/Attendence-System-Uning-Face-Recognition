# UI Navigation System: Sidebar Routing & Breadcrumbs

This document explains the page-switching architecture, sidebar menu definitions, and breadcrumb tracking used inside the application shell.

---

## 1. Routing Lifecycle

The system routes views using a registration pattern managed by the `NavigationManager` and `PageManager`.

```
[ User Clicks Sidebar Button (e.g., "Students") ]
                       |
                       v
[ NavigationManager.show_page("Students") Called ]
                       |
                       +----------------------------------------+
                       |                                        |
                       v                                        v
  [ Sets "Students" Button Active ]          [ PageManager.raise_page("Students") ]
  [ Deactivates other nav links   ]                             |
                                                                v
                                                [ Check if Instantiated in Cache? ]
                                                   /                           \
                                                 No                             Yes
                                                 /                               \
                                    [ Instantiate Page Frame ]              [ Raise Frame ]
                                    [ Grid Page View in Content Area ]            |
                                                 \                               /
                                                  +--------------+--------------+
                                                                 |
                                                                 v
                                             [ Update Header Breadcrumb Label ]
```

---

## 2. Menu Registry

The sidebar menu structure is defined dynamically as key-icon-class mappings.

The current registry includes the following views:

| Page Name | Icon | Target Phase | Description |
| :--- | :--- | :--- | :--- |
| **Dashboard** | 📊 | Phase 6 | System metrics overview and diagnostics console. |
| **Students** | 👥 | Phase 4 | Profiles registry, enrolment configurations. |
| **Faculty** | 👨‍🏫 | Phase 4 | Faculty lists and allocation mappings. |
| **Departments** | 🏢 | Phase 4 | Department registers. |
| **Courses** | 🎓 | Phase 4 | Course outlines and structures. |
| **Subjects** | 📘 | Phase 4 | Subject assignments. |
| **Dataset** | 📂 | Phase 5 | Student face capture and alignment pipeline. |
| **Camera** | 📷 | Phase 8 | Live camera streams and recognition overlays. |
| **Attendance** | 📝 | Phase 9 | Logs check-ins and session registries. |
| **Reports** | 📈 | Phase 10 | Exports PDF records and csv statistics sheets. |
| **Settings** | ⚙️ | Phase 0 | Confidence limits, camera ports, databases. |
| **About** | ℹ️ | Phase 1 | Versions, framework metadata, license checks. |
