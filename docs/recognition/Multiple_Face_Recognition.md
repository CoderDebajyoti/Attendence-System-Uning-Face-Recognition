# Multiple Face Recognition

This document describes how the engine handles multiple simultaneous faces.

## Multi-Face Support
The face recognition engine is fully capable of identifying multiple people in a single frame.

## Processing Pipeline
For any given camera frame containing $N$ faces:
1. `FaceDetectorService` detects all bounding boxes, yielding a list:
   $$[\text{box}_1, \text{box}_2, \dots, \text{box}_N]$$
2. For each box:
   - Crop, resize, and convert to grayscale.
   - Run LBPH classification independently.
   - Evaluate similarity against the threshold.
   - Compile a separate `RecognitionResult` dict.
3. The GUI receives the list of results and renders separate overlay boxes (with independent green/red colors and labels) for each person in the frame.
