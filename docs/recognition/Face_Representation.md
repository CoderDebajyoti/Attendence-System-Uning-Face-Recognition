# Face Representation

This document details the feature representation technique used in this system.

## Local Binary Patterns Histograms (LBPH)
LBPH maps local spatial micro-structures of face crops into feature vectors.

### Algorithm Summary
1. **LBP Operator**: For each pixel in the grayscale face crop, it compares its value with its 8 neighbors. If the neighbor's value is greater or equal to the center pixel, it is labeled as `1`, otherwise `0`. This gives an 8-bit binary number (e.g., `11001011`), which is converted to decimal (e.g., `203`).
2. **Dividing Grid**: The LBP image is divided into $8 \times 8$ or $16 \times 16$ local regions.
3. **Histogram Extraction**: A histogram of LBP values is calculated for each region.
4. **Concatenation**: All regional histograms are concatenated into a single global histogram representing the face features.

## Why LBPH?
- **Rotation & Illumination Invariance**: Grayscale LBP operators are highly robust to local lighting fluctuations and tilt angles.
- **Zero Heavy Weights**: Features are represented as small histogram grids on disk instead of floating point matrices of multi-million parameter neural networks, making it extremely lightweight and efficient.
