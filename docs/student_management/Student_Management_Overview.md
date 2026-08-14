# Student Management Module: Overview

This document provides a high-level overview of the **Student Management Module** implemented during Phase 7.

---

## 1. Functional Scope

The Student Management module maps student profiles into academic departments and courses, establishing the base relational structures.

The module supports the following workflows:
- **Profile Onboarding**: Capturing demographic, contact, and structural variables (Department, Course, Semester, Year).
- **CRUD Operations**: Enforcing unique parameters (Student IDs, Roll Numbers) and validating formats.
- **Biometric Synchronization Hooks**: Exposing dataset status metadata tags (`Not Registered`, `Collecting`, `Ready`, `Needs Update`) to coordinate with future camera capture modules.
- **Relational Integrity**: Linking students to departments and courses to preserve database normalizations (Third Normal Form).

---

## 2. Status Lifecycle Mappings

Students transition through academic states tracked inside the database:
- **Active**: Student is fully registered. Eligible for live recognition scans.
- **Inactive**: Disabled state (soft delete/leave of absence). Preserved in database for auditing.
- **Graduated**: Completed degree program. Read-only historical status.
- **Suspended**: Temporarily blocked due to disciplinary actions. Suppresses attendance logging.

---

## 3. Biometric Pipeline Preparation

This phase prepares the data layer for future biometric integrations:
- **`face_dataset_status`**: Tracks training status. Starts as `Not Registered`. Transitions to `Collecting` during crop sweeps, and `Ready` when the 512-D ONNX embedding vector is generated.
- **Relational Integrity**: The `face_embeddings` table references `students(id)` with cascade-delete constraints, guaranteeing that deleting a student profile cleans up raw crop files and vector blobs.
