# Biometric Privacy & Security

This document outlines security practices and data privacy standards implemented in this module.

## Core Security Rules
Since the system handles sensitive student biometrics, the following security constraints are enforced:

1. **No Raw Image Storage in DB**: Face photos are kept strictly in the local, non-public storage directory (`database/datasets/students/<student_code>/`) on the physical machine, never uploaded to a cloud database or checked into Git.
2. **Local Inference**: All face identification operations run locally on the client host. No biometric feature vectors or frames are transmitted over external networks.
3. **Privacy-safe Logs**: Bounding boxes, similarity scores, processing latencies, and classification matches are logged for diagnostics. Raw facial landmarks, image files, or biometric histograms are **never** logged to text logs.
4. **Git Isolation**: The model XML file (`models/recognition_model.xml`) and student datasets are ignored via `.gitignore` to prevent leakage to code repositories.
