# Image Processing Service

This document describes how raw camera frames are cropped, normalized, and saved as training crops in the `ImageProcessingService`.

---

## Processing Flow

```
[Raw Frame BGR]
       │
       ├─► [Crop coordinates] ──► Crop region of interest (ROI)
       │
       ├─► [Resize] ────────────► Rescale to exactly 112x112 (INTER_AREA)
       │
       ├─► [Grayscale] ─────────► Compute mean pixel value (Brightness Audit)
       │
       ├─► [Laplacian] ─────────► Evaluate variance (Blurriness Audit)
       │
       ▼ (All checks passed)
[Save as image_xxx.jpg]
```

---

## Detailed Pipeline Steps

### 1. Cropping & Boundary Safety
The bounding box coordinates are clamped to the image boundaries to prevent errors if the bounding box values are slightly outside the frame:
$$\text{x\_start} = \max(0, x), \quad \text{y\_start} = \max(0, y)$$

### 2. Resizing & Interpolation
Crops are resized to a standard alignment dimension of **112x112** pixels using bilinear area interpolation (`cv2.INTER_AREA`), which is ideal for downsampling and maintains details.

### 3. Brightness Audit
Converts the crop to grayscale and calculates the mean pixel value:
*   **Too Dark**: Mean value $< 45$ (triggers warning "Face crop is too dark. Please improve lighting.").
*   **Too Bright**: Mean value $> 230$ (triggers warning "Face crop is too bright. Please reduce glare.").

### 4. Blurriness (Sharpness) Audit
Applies the Laplacian operator to calculate the variance. A higher variance indicates sharper transitions and edges:
*   **Too Blurry**: Variance $< 50.0$ (triggers warning "Image is too blurry. Please remain still.").
