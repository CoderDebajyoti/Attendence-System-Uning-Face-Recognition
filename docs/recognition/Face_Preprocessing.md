# Face Preprocessing

This document outlines the face image preprocessing pipeline.

## Determinism
To maximize matching accuracy, the same preprocessing logic is applied during both:
1. **Dataset Collection** (saving face templates).
2. **Live Viewfinder Recognition** (inference).

## Pipeline Steps

### 1. Bounding Box Crop
Given a bounding box `(x, y, w, h)`, the face region is sliced from the BGR image. Crop bounds are clamped to prevent out-of-boundary indexing crashes:
```python
x_start = max(0, x)
y_start = max(0, y)
x_end = min(width, x + w)
y_end = min(height, y + h)
crop = image[y_start:y_end, x_start:x_end]
```

### 2. Resize
The cropped BGR face is resized to `112x112` using bilinear interpolation (`cv2.INTER_AREA`), matching standard ArcFace/InsightFace input dimensions:
```python
resized = cv2.resize(crop, (112, 112), interpolation=cv2.INTER_AREA)
```

### 3. Grayscale Conversion
LBPH requires 1-channel grayscale inputs. BGR crops are converted:
```python
gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
```
This reduces channel-wide computational overhead and normalizes color differences.
