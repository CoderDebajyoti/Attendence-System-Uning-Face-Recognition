# Face Dataset Storage Structure

This document describes the filesystem layout, directory rules, and Git exclusions for facial image datasets.

---

## Workspace Folder Layout

All training crops are saved under the path configured in `settings.dataset_path` (defaults to `database/datasets`).

The directory structure is organized by student code to ensure human-readability:

```
database/datasets/
└── students/
    ├── STD2026001/
    │   ├── image_001.jpg
    │   ├── image_002.jpg
    │   └── image_025.jpg
    └── STD2026002/
        ├── image_001.jpg
        └── image_002.jpg
```

---

## File Naming Conventions

*   **Directories**: Named using the unique, uppercase `Student.student_code` (e.g. `STD2026001`). This prevents filename collisions and keeps files organized.
*   **Images**: Named sequentially using a zero-padded index (e.g. `image_001.jpg`, `image_002.jpg`). The system checks existing files to determine the next index.

---

## Git Exclusion Rules

Biometric images are sensitive and must not be pushed to public Git repositories.

The project's `.gitignore` contains the following rule:
```
database/datasets/*
```
This rule excludes all dataset subfolders and files from version control.
