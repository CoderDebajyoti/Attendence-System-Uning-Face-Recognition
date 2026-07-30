# Face Recognition Attendance System - Testing Plan

This testing plan defines the validation strategy for the Face Recognition Attendance System to verify that all functional and non-functional requirements are met before release.

---

## 1. Testing Hierarchy Matrix

The table below outlines our testing levels, tools, and coverage objectives:

| Level | Testing Area | Tools Used | Objectives |
| :--- | :--- | :--- | :--- |
| **Unit Testing** | Individual classes, utility functions, business rules. | `pytest`, `unittest.mock` | Validate algorithms (e.g., similarity calculations, date filters, validation logic) in isolation. |
| **Integration Testing**| Interaction between layers (Services, Repositories, DB). | `pytest`, SQLite In-Memory | Ensure database transactions execute, roll back, and constraint rules function as expected. |
| **System Testing** | End-to-end user journeys (User Flow testing). | Manual scripts, `pytest-patched` UI | Verify view navigation, capture wizards, and scanner operations. |
| **Performance Testing**| Computational bounds, memory leaks, framerates. | `cProfile`, `memory_profiler` | Enforce $<150\text{ms}$ recognition latencies and $\ge 30\text{ FPS}$ UI thread execution. |
| **Accuracy Testing** | Face recognition thresholds and error bounds. | Labelled LFW dataset slice | Calculate Precision, Recall, and F1-score to tune threshold parameter targets. |
| **Hardware Testing** | Camera dropouts, source swaps, IP stream lag. | Mock RTSP/V4L loops | Ensure graceful recovery and user messaging when input feeds disconnect. |

---

## 2. Core Testing Strategies

### 2.1 Unit Testing & Dependency Mocking
- **Face Engine Mocking**: Since calling ONNX models consumes significant CPU, unit tests mock `IFaceEngine` to return predictable bounding boxes and dummy 512-dimensional arrays.
  ```python
  # Example PyTest fixture mocking the Face Engine
  import pytest
  import numpy as np
  from unittest.mock import MagicMock
  from src.core.interfaces.face_engine import IFaceEngine

  @pytest.fixture
  def mock_face_engine():
      engine = MagicMock(spec=IFaceEngine)
      engine.detect_faces.return_value = [{"box": [10, 10, 100, 100], "landmarks": []}]
      engine.align_face.return_value = np.zeros((112, 112, 3), dtype=np.uint8)
      engine.extract_embedding.return_value = np.random.randn(512)
      return engine
  ```

### 2.2 Integration Testing (In-Memory Database)
- To prevent tests from dirtying the local development database (`data/app_database.db`), we configure SQLAlchemy to spin up an in-memory SQLite instance for tests:
  ```python
  # pytest db setup fixture
  from sqlalchemy import create_engine
  from sqlalchemy.orm import sessionmaker
  from src.data_access.models import DeclarativeBase

  @pytest.fixture
  def in_memory_db():
      engine = create_engine("sqlite:///:memory:")
      DeclarativeBase.metadata.create_all(engine)
      Session = sessionmaker(bind=engine)
      session = Session()
      yield session
      session.close()
  ```

### 2.3 Camera & Video Pipeline Simulation
- To test the background thread processing without a live USB camera attached, we construct a virtual video source:
  1. A pre-recorded video file containing walking/turning faces is saved under `tests/resources/simulated_stream.mp4`.
  2. The configuration is set to read this file path instead of camera index `0`.
  3. The test verifies that the worker threads fetch frames, process faces, and write records to the log queue.

### 2.4 Recognition Accuracy Benchmarking
- **Dataset**: A subset of the public **Labeled Faces in the Wild (LFW)** dataset is kept in the testing resources.
- **Tuning Process**: The test suite runs a test script comparing pairs of images:
  - **Positive Pairs**: Two different photos of the same individual (should match).
  - **Negative Pairs**: Photos of two different individuals (should not match).
- **Metrics Calculated**:
  - **True Positive Rate (TPR / Sensitivity)**: Correctly matched students.
  - **False Positive Rate (FPR / Buddy Punching Risk)**: Mismatched identities (must be strictly $<0.01\%$ in production configuration).
  - **F1-Score Evaluation**: Curve optimization used to set the default cosine threshold limit to `0.65`.

### 2.5 Performance Constraints
Automated performance checks profile the following operations:
1. **Model Loading Time**: Importing and loading ONNX runtimes must complete within $<5$ seconds.
2. **Inference Latency**: Running RetinaFace detection + ArcFace extraction must execute within $<120\text{ms}$ on a standard 4-core Intel i5 CPU.
3. **Memory Stability**: The app must not exceed a baseline footprint of $450\text{MB}$ RAM during continuous 2-hour video scans (verifying OpenCV frame garbage collection).
