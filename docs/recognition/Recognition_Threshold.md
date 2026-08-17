# Recognition Threshold

This document describes the role of the recognition threshold.

## Central Configuration
The threshold is defined in the `.env` configuration file:
```env
RECOGNITION_THRESHOLD=0.65
```
This is loaded as a float property in the type-safe configuration settings.

## Threshold Interpretation
- **Higher Threshold (e.g. 0.75 - 0.85)**:
  - Requires a closer histogram match (lower Chi-Square distance).
  - *Effect*: Reduces **False Acceptances** (unregistered people mistakenly identified as students), but increases **False Rejections** (valid students failed to be identified).
- **Lower Threshold (e.g. 0.50 - 0.60)**:
  - Accepts a looser histogram match (higher Chi-Square distance).
  - *Effect*: Reduces **False Rejections** (easier matching for valid students under poor lighting), but increases **False Acceptances**.
- **Default (0.65)**: Optimal calibration balancing accuracy and convenience in typical classroom ambient light.
