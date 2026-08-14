# Camera Stream Integration

This document describes how video streams are captured using OpenCV, processed in background threads, and rendered smoothly inside CustomTkinter.

---

## Multithreaded Feed Architecture

To prevent GUI freezing, the system decouples frame capture (blocking I/O) from rendering (main event loop):

```
[Camera Hardware]
       │
       ▼ (blocking read)
┌──────────────────────────────┐
│  CameraReader (Thread-0)     │  <--- Continuously loops cap.read()
└──────────────────────────────┘
       │
       ▼ (atomic reference updates)
   latest_frame (cv2 ndarray)
       │
       ▼ (polled every 33ms)
┌──────────────────────────────┐
│  DatasetPage (Main UI)       │  <--- Schedules updates via self.after()
└──────────────────────────────┘
```

---

## Graceful Exception Handling

The system catches camera errors to prevent application crashes:

1. **Camera Unavailable**: If `cv2.VideoCapture` fails to bind, the thread signals `error_occurred = True` and terminates cleanly.
2. **Disconnected Feed**: If `cap.read()` returns `ret = False` during execution, the loop exits and alerts the user in the status bar.
3. **Invalid Index / RTSP URL**: Evaluates config bounds before startup. Uses fallback ID 0 if custom RTSP streams fail.

---

## Automatic Resource Release

To prevent locking the camera device for other programs, resources are released when:
*   The page is hidden or mapped out of view (monitored by checking `self.winfo_ismapped()`).
*   The user clicks **Stop Camera** or **Finish**.
*   The application page is destroyed or closed (handled via `destroy()` hooks).
