# Face Recognition Pipeline

This document details the operations performed at each stage of the recognition pipeline.

## Flow of Operations

```mermaid
sequenceDiagram
    participant Camera
    participant Detector
    participant Preprocessor
    participant Recognizer
    participant Repositories
    participant GUI

    Camera->>Detector: BGR Frame
    Detector->>Detector: Haar Cascade face detection
    Detector->>Preprocessor: Bounding Box (x, y, w, h)
    Preprocessor->>Preprocessor: Crop & Resize (112x112)
    Preprocessor->>Preprocessor: Convert to Grayscale
    Preprocessor->>Recognizer: Preprocessed Gray Face
    Recognizer->>Recognizer: Predict using LBPH model
    Recognizer->>Recognizer: Map distance to similarity
    Recognizer->>Repositories: Fetch Student (if similarity >= threshold)
    Repositories-->>Recognizer: Student Record
    Recognizer-->>GUI: Structured RecognitionResult
    GUI->>GUI: Render viewfinder overlays
```

### Modular Steps
- **Frame Grab**: Background camera reader thread updates BGR frames.
- **Detection**: Haar cascade matches face candidates.
- **Preprocessing**: Slices bounding box, resizes to 112x112, and grayscales.
- **Classification**: LBPH predicts label and similarity.
- **ID Mapping**: Database retrieves full student profile.
- **UI Drawing**: Visual bounding box, label text, and status tags are drawn.
