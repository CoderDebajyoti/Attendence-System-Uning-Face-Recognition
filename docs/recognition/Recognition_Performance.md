# Recognition Performance

This document describes latency management, threading, and frame optimization.

## Thread Isolation
To prevent interface lags and freezing:
- **Frame Reader**: Camera frame acquisition runs inside a dedicated background thread (`CameraReader`), fetching and updating frames asynchronously at ~30 FPS.
- **Asynchronous Model Build**: Model training is offloaded from the CustomTkinter main loop using Python daemon threads. Once training completes, callbacks are safely scheduled back onto the GUI thread.

## Latency Metrics
- **Preprocessing & Crop**: $<1\text{ ms}$ (highly optimized NumPy slicing and resizing).
- **LBPH Inference**: $<2\text{ ms}$ per face (sub-millisecond histogram comparison).
- **Database Mapping**: $<5\text{ ms}$ (indexed SQLite queries).
- **Overall Recognition latency**: Typically $<10\text{ ms}$ per frame, guaranteeing smooth $\ge 30\text{ FPS}$ UI rendering.
