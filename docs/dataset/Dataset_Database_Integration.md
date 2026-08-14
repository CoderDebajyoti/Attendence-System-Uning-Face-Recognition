# Database Integration Schema

This document explains the schema design, tables, relationships, and queries used to manage face dataset metadata.

---

## Schema Model relationships

The entity relationship diagram for the face dataset module:

```mermaid
erDiagram
    STUDENTS ||--|| FACE_DATASETS : has
    FACE_DATASETS ||--o{ DATASET_IMAGES : contains

    STUDENTS {
        int id PK
        varchar student_code UK
        varchar face_dataset_status
    }
    
    FACE_DATASETS {
        int id PK
        int student_id FK
        varchar dataset_path
        int image_count
        varchar status
        datetime created_at
        datetime updated_at
        datetime last_validation
        varchar validation_result
    }
    
    DATASET_IMAGES {
        int id PK
        int dataset_id FK
        varchar file_path
        datetime created_at
    }
```

---

## Key SQL Constraints

1.  **Cascading Deletes**: `ondelete="CASCADE"` is set on the foreign keys `student_id` in `face_datasets` and `dataset_id` in `dataset_images`. Deleting a student record automatically deletes their dataset and images metadata rows.
2.  **Unique Constraints**: `student_id` is unique in `face_datasets` (one-to-one relationship), and `file_path` is unique in `dataset_images` to prevent file path duplicates.
3.  **Automatic Seeding**: Tables are generated on start via SQLAlchemy `Base.metadata.create_all(_engine)` in `database.py`.
