# ==============================================================================
# Face Recognition Attendance System - Face Recognition Page View
# ==============================================================================

import customtkinter as ctk
import cv2
import time
import logging
from PIL import Image
from src.gui.pages.base import BasePage
from src.gui.themes import ThemeManager
from src.gui.components import Card, MessageBox
from src.gui.pages.dataset import CameraReader
from src.controllers.recognition_controller import RecognitionController
from src.controllers.attendance_controller import AttendanceController
from src.core import constants

logger = logging.getLogger("app.gui")

class RecognitionPage(BasePage):
    """
    Face Recognition Page View. Implements Phase 9 Face Recognition Engine.
    Includes model status dashboard, async model building controls,
    live camera preview, multi-face tracking overlays, and recognition telemetry.
    """
    def __init__(self, parent, controller) -> None:
        self.recognition_controller = RecognitionController()
        self.camera_reader = None
        self.update_loop_id = None
        self.is_camera_active = False
        self.recognition_enabled = True

        # Telemetry metrics
        self.fps_avg = 0.0
        self.latency_avg = 0.0
        self.face_count = 0
        self.last_frame_time = time.perf_counter()
        
        # Attendance tracking
        self.attendance_controller = AttendanceController()
        self.pending_confirmation_student_id = None
        self.pending_recognition_result = None

        super().__init__(
            parent=parent,
            controller=controller,
            title="Biometric Recognition Engine",
            description="Run live face recognition streams, manage biometric indices, and monitor classification parameters.",
            phase=9
        )

    def show_default_placeholder(self) -> None:
        """
        Overrides the base class placeholder to render the full Recognition interface.
        """
        # Configure layout grid
        self.content_frame.grid_columnconfigure(0, weight=4)  # Left panel (40%)
        self.content_frame.grid_columnconfigure(1, weight=6)  # Right panel (60%)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # 1. Left side panel (Model & Engine status, controls)
        self.left_panel = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, ThemeManager.PAD_MD))
        self.left_panel.grid_columnconfigure(0, weight=1)

        self.create_model_status_card()
        self.create_controls_card()
        self.create_telemetry_card()
        self.create_attendance_status_card()

        # 2. Right side panel (Camera preview, live overlays)
        self.right_panel = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(ThemeManager.PAD_MD, 0))
        self.right_panel.grid_columnconfigure(0, weight=1)
        self.right_panel.grid_rowconfigure(0, weight=1)

        self.create_camera_card()

        # Load initial model status on GUI
        self.refresh_model_status()

        # Bind visibility change check
        self.check_visibility()

    def check_visibility(self) -> None:
        """
        Periodically checks if the page is visible. Stops camera if navigating away.
        """
        if not self.winfo_ismapped() and self.is_camera_active:
            logger.info("RecognitionPage hidden. Automatically stopping camera stream.")
            self.stop_camera()
        self.after(1000, self.check_visibility)

    def create_model_status_card(self) -> None:
        """
        Renders the model training status and metadata dashboard.
        """
        self.status_card = Card(self.left_panel)
        self.status_card.grid(row=0, column=0, sticky="ew", pady=(0, ThemeManager.PAD_SM))
        self.status_card.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(
            self.status_card,
            text="Biometric Model Status",
            font=ThemeManager.get_font(size=12, weight="bold"),
            text_color=ThemeManager.get_color("accent_primary")
        )
        title.grid(row=0, column=0, columnspan=2, sticky="w", padx=ThemeManager.PAD_MD, pady=(ThemeManager.PAD_SM, ThemeManager.PAD_XS))

        self.status_labels = {}
        info_rows = [
            ("Model Status", "Loading..."),
            ("Registered Students", "-"),
            ("Trained Images", "-"),
            ("Last Built", "-")
        ]

        for idx, (label_name, default_val) in enumerate(info_rows):
            lbl_key = ctk.CTkLabel(
                self.status_card,
                text=f"{label_name}:",
                font=ThemeManager.get_font(size=11, weight="bold"),
                text_color=ThemeManager.get_color("text_muted")
            )
            lbl_key.grid(row=idx+1, column=0, sticky="w", padx=ThemeManager.PAD_MD, pady=2)

            lbl_val = ctk.CTkLabel(
                self.status_card,
                text=default_val,
                font=ThemeManager.get_font(size=11),
                text_color=ThemeManager.get_color("text_primary")
            )
            lbl_val.grid(row=idx+1, column=1, sticky="w", padx=ThemeManager.PAD_MD, pady=2)
            self.status_labels[label_name] = lbl_val

        # Add Build / Rebuild buttons
        btn_frame = ctk.CTkFrame(self.status_card, fg_color="transparent")
        btn_frame.grid(row=5, column=0, columnspan=2, sticky="ew", padx=ThemeManager.PAD_MD, pady=ThemeManager.PAD_MD)
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        self.build_btn = ctk.CTkButton(
            btn_frame,
            text="Build Model",
            font=ThemeManager.get_font(size=11, weight="bold"),
            fg_color=ThemeManager.get_color("accent_primary"),
            text_color=ThemeManager.get_color("text_dark"),
            hover_color=ThemeManager.get_color("bg_active"),
            command=self.start_model_build
        )
        self.build_btn.grid(row=0, column=0, padx=2, sticky="ew")

        self.refresh_btn = ctk.CTkButton(
            btn_frame,
            text="Refresh Status",
            font=ThemeManager.get_font(size=11),
            fg_color=ThemeManager.get_color("bg_active"),
            text_color=ThemeManager.get_color("text_primary"),
            hover_color=ThemeManager.get_color("bg_card"),
            command=self.refresh_model_status
        )
        self.refresh_btn.grid(row=0, column=1, padx=2, sticky="ew")

    def create_controls_card(self) -> None:
        """
        Renders live camera control options and recognition toggle switches.
        """
        card = Card(self.left_panel)
        card.grid(row=1, column=0, sticky="ew", pady=ThemeManager.PAD_SM)
        card.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            card,
            text="Engine Controls",
            font=ThemeManager.get_font(size=12, weight="bold"),
            text_color=ThemeManager.get_color("accent_primary")
        )
        title.grid(row=0, column=0, sticky="w", padx=ThemeManager.PAD_MD, pady=(ThemeManager.PAD_SM, ThemeManager.PAD_XS))

        # Toggle recognition switch
        self.rec_switch = ctk.CTkSwitch(
            card,
            text="Face Recognition ON",
            font=ThemeManager.get_font(size=11),
            text_color=ThemeManager.get_color("text_primary"),
            progress_color=ThemeManager.get_color("accent_success"),
            command=self.toggle_recognition
        )
        self.rec_switch.select() # Enabled by default
        self.rec_switch.grid(row=1, column=0, sticky="w", padx=ThemeManager.PAD_MD, pady=ThemeManager.PAD_SM)

        # Start / Stop camera buttons
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=ThemeManager.PAD_MD, pady=ThemeManager.PAD_MD)
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        self.start_btn = ctk.CTkButton(
            btn_frame,
            text="Start Camera",
            font=ThemeManager.get_font(size=11, weight="bold"),
            fg_color=ThemeManager.get_color("accent_success"),
            text_color=ThemeManager.get_color("text_dark"),
            hover_color=ThemeManager.get_color("bg_active"),
            command=self.start_camera
        )
        self.start_btn.grid(row=0, column=0, padx=2, sticky="ew")

        self.stop_btn = ctk.CTkButton(
            btn_frame,
            text="Stop Camera",
            font=ThemeManager.get_font(size=11, weight="bold"),
            fg_color=ThemeManager.get_color("accent_danger"),
            text_color=ThemeManager.get_color("text_light"),
            hover_color=ThemeManager.get_color("bg_card"),
            state="disabled",
            command=self.stop_camera
        )
        self.stop_btn.grid(row=0, column=1, padx=2, sticky="ew")

    def create_telemetry_card(self) -> None:
        """
        Renders real-time computational telemetry metrics.
        """
        self.telemetry_card = Card(self.left_panel)
        self.telemetry_card.grid(row=2, column=0, sticky="ew", pady=ThemeManager.PAD_SM)
        self.telemetry_card.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(
            self.telemetry_card,
            text="Engine Telemetry",
            font=ThemeManager.get_font(size=12, weight="bold"),
            text_color=ThemeManager.get_color("accent_primary")
        )
        title.grid(row=0, column=0, columnspan=2, sticky="w", padx=ThemeManager.PAD_MD, pady=(ThemeManager.PAD_SM, ThemeManager.PAD_XS))

        self.telemetry_labels = {}
        metrics = [
            ("Faces Detected", "0"),
            ("Match Latency", "0.0 ms"),
            ("Frame Rate", "0.0 FPS"),
            ("Threshold Config", "0.65")
        ]

        for idx, (label_name, default_val) in enumerate(metrics):
            lbl_key = ctk.CTkLabel(
                self.telemetry_card,
                text=f"{label_name}:",
                font=ThemeManager.get_font(size=11, weight="bold"),
                text_color=ThemeManager.get_color("text_muted")
            )
            lbl_key.grid(row=idx+1, column=0, sticky="w", padx=ThemeManager.PAD_MD, pady=2)

            lbl_val = ctk.CTkLabel(
                self.telemetry_card,
                text=default_val,
                font=ThemeManager.get_font(size=11),
                text_color=ThemeManager.get_color("text_primary")
            )
            lbl_val.grid(row=idx+1, column=1, sticky="w", padx=ThemeManager.PAD_MD, pady=2)
            self.telemetry_labels[label_name] = lbl_val

        threshold = self.recognition_controller.get_configured_threshold()
        self.telemetry_labels["Threshold Config"].configure(text=f"{threshold} (LBPH)")

    def create_camera_card(self) -> None:
        """
        Renders right side camera canvas panel.
        """
        card = Card(self.right_panel)
        card.grid(row=0, column=0, sticky="nsew")
        card.grid_rowconfigure(1, weight=1)
        card.grid_columnconfigure(0, weight=1)

        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=ThemeManager.PAD_MD, pady=(ThemeManager.PAD_SM, ThemeManager.PAD_XS))
        
        title = ctk.CTkLabel(
            header_frame,
            text="Live Recognition Viewfinder",
            font=ThemeManager.get_font(size=12, weight="bold"),
            text_color=ThemeManager.get_color("accent_primary")
        )
        title.pack(side="left")

        self.feed_status_lbl = ctk.CTkLabel(
            header_frame,
            text="Stream: Offline",
            font=ThemeManager.get_font(size=11, weight="bold"),
            text_color=ThemeManager.get_color("text_muted")
        )
        self.feed_status_lbl.pack(side="right")

        # Live viewfinder canvas label container
        self.preview_lbl = ctk.CTkLabel(
            card,
            text="Camera Stream Inactive\nClick 'Start Camera' to load viewfinder feed.",
            font=ThemeManager.get_font(size=12),
            text_color=ThemeManager.get_color("text_muted"),
            fg_color=ThemeManager.get_color("bg_main")
        )
        self.preview_lbl.grid(row=1, column=0, sticky="nsew", padx=ThemeManager.PAD_MD, pady=(0, ThemeManager.PAD_MD))

    def refresh_model_status(self) -> None:
        """
        Fetches current status of model files and displays info in GUI.
        """
        status = self.recognition_controller.get_model_status()
        metadata = self.recognition_controller.get_model_metadata()

        status_colors = {
            "READY": ThemeManager.get_color("accent_success"),
            "OUTDATED": ThemeManager.get_color("accent_warning"),
            "BUILDING": ThemeManager.get_color("accent_warning"),
            "INVALID": ThemeManager.get_color("accent_danger"),
            "NOT_BUILT": ThemeManager.get_color("accent_danger")
        }
        
        status_text = status.replace("_", " ")
        self.status_labels["Model Status"].configure(
            text=status_text,
            text_color=status_colors.get(status, ThemeManager.get_color("text_primary"))
        )

        if status in ("READY", "OUTDATED") and metadata:
            self.status_labels["Registered Students"].configure(text=str(metadata.get("student_count", 0)))
            self.status_labels["Trained Images"].configure(text=str(metadata.get("image_count", 0)))
            
            created_at_str = metadata.get("created_at", "-")
            try:
                dt = datetime.fromisoformat(created_at_str)
                display_date = dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                display_date = created_at_str
                
            self.status_labels["Last Built"].configure(text=display_date)
            self.build_btn.configure(text="Rebuild Model")
        else:
            self.status_labels["Registered Students"].configure(text="-")
            self.status_labels["Trained Images"].configure(text="-")
            self.status_labels["Last Built"].configure(text="-")
            self.build_btn.configure(text="Build Model")

        # Update core GUI status metrics
        app = self.controller
        if hasattr(app, "initialize_status_metrics"):
            app.initialize_status_metrics()

    def start_model_build(self) -> None:
        """
        Triggered when clicking Build/Rebuild Model. Trains model in background thread.
        """
        self.build_btn.configure(state="disabled")
        self.status_labels["Model Status"].configure(text="BUILDING", text_color=ThemeManager.get_color("accent_warning"))
        
        # Disable inputs
        self.refresh_btn.configure(state="disabled")

        def on_complete(report):
            self.build_btn.configure(state="normal")
            self.refresh_btn.configure(state="normal")
            
            if report["success"]:
                MessageBox.show_info(
                    self, 
                    title="Build Completed", 
                    message=f"Model successfully built!\nStudents included: {report['students_included']}\nImages included: {report['images_included']}"
                )
            else:
                MessageBox.show_error(
                    self, 
                    title="Build Failed", 
                    message=f"Could not build model: {report['error'] or 'Unknown error'}"
                )
            self.refresh_model_status()

        self.recognition_controller.build_model_async(self, on_complete)

    def toggle_recognition(self) -> None:
        """
        Handles toggling face recognition ON/OFF.
        """
        self.recognition_enabled = self.rec_switch.get()
        logger.info(f"Biometrics recognition enabled state: {self.recognition_enabled}")

    def start_camera(self) -> None:
        """
        Spawns background CameraReader thread and opens stream.
        """
        if self.is_camera_active:
            return

        source = self.recognition_controller.get_camera_source()
        self.camera_reader = CameraReader(source)
        
        self.feed_status_lbl.configure(text="Stream: Connecting...", text_color=ThemeManager.get_color("accent_warning"))
        self.start_btn.configure(state="disabled")
        self.build_btn.configure(state="disabled")

        # Run background thread
        self.camera_reader.start()
        self.is_camera_active = True
        
        # Wait for camera initialization
        self.check_camera_startup()

    def check_camera_startup(self) -> None:
        """
        Monitors startup status of camera capture stream thread.
        """
        if not self.is_camera_active or not self.camera_reader:
            return

        if self.camera_reader.error_occurred:
            err = self.camera_reader.error_message
            MessageBox.show_error(self, title="Camera Connection Failure", message=err)
            self.stop_camera()
            return

        # Check if the thread has fetched its first valid frame
        if self.camera_reader.latest_frame is not None:
            self.feed_status_lbl.configure(text="Stream: Active (Live)", text_color=ThemeManager.get_color("accent_success"))
            self.stop_btn.configure(state="normal")
            self.preview_lbl.configure(text="")
            
            # Reset FPS telemetry timer
            self.last_frame_time = time.perf_counter()
            self.fps_avg = 0.0
            self.latency_avg = 0.0
            
            # Start UI feed loop
            self.update_camera_frame_loop()
        else:
            # Not loaded yet, query again shortly
            self.after(100, self.check_camera_startup)

    def update_camera_frame_loop(self) -> None:
        """
        Viewfinder frame capture, face detection, pre-processing, recognition, and overlays.
        """
        if not self.is_camera_active or not self.camera_reader:
            return

        frame = self.camera_reader.latest_frame
        if frame is not None:
            try:
                # Calculate FPS telemetry
                now = time.perf_counter()
                elapsed = now - self.last_frame_time
                self.last_frame_time = now
                fps = 1.0 / elapsed if elapsed > 0 else 0
                self.fps_avg = 0.9 * self.fps_avg + 0.1 * fps

                # Clone frame for UI drawings
                display_frame = frame.copy()
                
                # Fetch detector instance from dataset controller service
                from src.services.face_detector_service import FaceDetectorService
                detector = FaceDetectorService.get_instance() if hasattr(FaceDetectorService, "get_instance") else FaceDetectorService()
                
                # 1. Run Face Detection
                boxes = detector.detect_faces(display_frame)
                self.face_count = len(boxes)

                latency_val = 0.0
                model_status = self.recognition_controller.get_model_status()

                # 2. Run Face Recognition (if toggled ON and model exists)
                if self.recognition_enabled and boxes and model_status in ("READY", "OUTDATED"):
                    results = self.recognition_controller.recognize_frame(display_frame, boxes)
                    
                    # Accumulate match latencies for display
                    if results:
                        latency_val = sum(r["processing_time"] for r in results) / len(results)
                        self.latency_avg = 0.9 * self.latency_avg + 0.1 * latency_val

                    # Draw boxes with student profiles
                    for res in results:
                        x, y, w, h = res["bounding_box"]
                        
                        if res["recognized"]:
                            # Green overlay for successful recognized student
                            color = (0, 255, 0)
                            label_lines = [
                                res["student_name"],
                                f"ID: {res['student_code']}",
                                f"Match: {res['distance_or_similarity']:.2f}"
                            ]
                        else:
                            # Orange/Red overlay for unknown/unregistered person
                            color = (0, 0, 255)
                            label_lines = [
                                "Unknown",
                                "Not Registered"
                            ]

                        # Draw bounding box rectangle
                        cv2.rectangle(display_frame, (x, y), (x + w, y + h), color, 2)
                        
                        # Draw name tag box label
                        text_x = x
                        text_y = y - 10 if y - 10 > 20 else y + h + 20
                        
                        for i, line in enumerate(label_lines):
                            cv2.putText(
                                display_frame,
                                line,
                                (text_x, text_y + (i * 15)),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.4,
                                color,
                                1,
                                cv2.LINE_AA
                            )
                    # Integrate attendance tracking
                    recognized_any = False
                    for res in results:
                        if res["recognized"]:
                            self.handle_recognition_event(res)
                            recognized_any = True

                    if not recognized_any:
                        # If there is at least one face but none is recognized, show "Unknown"
                        for res in results:
                            if not res["recognized"]:
                                self.att_student_name_val.configure(text="Unknown Person", text_color=ThemeManager.get_color("accent_danger"))
                                self.att_student_code_val.configure(text="Confidence insufficient or not registered", text_color=ThemeManager.get_color("text_muted"))
                                self.att_status_lbl.configure(
                                    text="⚠ NOT RECORDED",
                                    text_color=ThemeManager.get_color("text_light"),
                                    fg_color=ThemeManager.get_color("accent_danger")
                                )
                                self.confirm_att_btn.configure(state="disabled")
                                self.cancel_att_btn.configure(state="disabled")
                                break
                else:
                    # Draw simple yellow boxes for generic face detection if recognition is off
                    color = (0, 200, 255) # Orange/Yellow
                    for x, y, w, h in boxes:
                        cv2.rectangle(display_frame, (x, y), (x + w, y + h), color, 2)
                        cv2.putText(
                            display_frame,
                            "Face Detected",
                            (x, y - 8),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.4,
                            color,
                            1,
                            cv2.LINE_AA
                        )
                    # Clear attendance UI state when recognition is off
                    self.show_attendance_feedback(None, status_type="idle")

                if not boxes:
                    # Clear attendance UI state if no boxes in frame
                    self.show_attendance_feedback(None, status_type="idle")

                # Write telemetry fields on dashboard
                self.telemetry_labels["Faces Detected"].configure(text=str(self.face_count))
                self.telemetry_labels["Match Latency"].configure(text=f"{self.latency_avg:.1f} ms" if self.recognition_enabled else "N/A (ON/OFF)")
                self.telemetry_labels["Frame Rate"].configure(text=f"{self.fps_avg:.1f} FPS")

                # Convert BGR to RGB and resize to fit preview widget (400x300 target size)
                rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                h_target, w_target = 300, 400
                pil_img = Image.fromarray(rgb_frame)
                pil_img = pil_img.resize((w_target, h_target), Image.Resampling.LANCZOS)
                
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(w_target, h_target))
                self.preview_lbl.configure(image=ctk_img, text="")

            except Exception as e:
                logger.error(f"Error rendering live recognition viewfinder frame: {e}")

        # Schedule next update frame (approx 30 FPS targeting 33ms delays)
        self.update_loop_id = self.after(33, self.update_camera_frame_loop)

    def stop_camera(self) -> None:
        """
        Safely halts update loops, stops camera threads, and releases resources.
        """
        self.is_camera_active = False

        if self.update_loop_id:
            self.after_cancel(self.update_loop_id)
            self.update_loop_id = None

        if self.camera_reader:
            self.camera_reader.stop()
            self.camera_reader = None

        self.feed_status_lbl.configure(text="Stream: Offline", text_color=ThemeManager.get_color("text_muted"))
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.build_btn.configure(state="normal")
        self.preview_lbl.configure(
            image=None, 
            text="Camera Stream Inactive\nClick 'Start Camera' to load viewfinder feed."
        )

        # Clear telemetry displays
        self.telemetry_labels["Faces Detected"].configure(text="0")
        self.telemetry_labels["Match Latency"].configure(text="0.0 ms")
        self.telemetry_labels["Frame Rate"].configure(text="0.0 FPS")
        self.show_attendance_feedback(None, status_type="idle")

    def create_attendance_status_card(self) -> None:
        """
        Renders the card displaying the current recognized student and status feedback.
        """
        self.attendance_card = Card(self.left_panel)
        self.attendance_card.grid(row=3, column=0, sticky="ew", pady=ThemeManager.PAD_SM)
        self.attendance_card.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(
            self.attendance_card,
            text="Attendance Logging Status",
            font=ThemeManager.get_font(size=12, weight="bold"),
            text_color=ThemeManager.get_color("accent_primary")
        )
        title.grid(row=0, column=0, columnspan=2, sticky="w", padx=ThemeManager.PAD_MD, pady=(ThemeManager.PAD_SM, ThemeManager.PAD_XS))

        self.att_student_name_val = ctk.CTkLabel(self.attendance_card, text="No detection", font=ThemeManager.get_font(size=13, weight="bold"), text_color=ThemeManager.get_color("text_muted"))
        self.att_student_name_val.grid(row=1, column=0, columnspan=2, sticky="w", padx=ThemeManager.PAD_MD, pady=2)

        self.att_student_code_val = ctk.CTkLabel(self.attendance_card, text="-", font=ThemeManager.get_font(size=11), text_color=ThemeManager.get_color("text_muted"))
        self.att_student_code_val.grid(row=2, column=0, columnspan=2, sticky="w", padx=ThemeManager.PAD_MD, pady=2)

        # Telemetry metrics check
        self.att_status_lbl = ctk.CTkLabel(
            self.attendance_card,
            text="STATUS: Idle",
            font=ThemeManager.get_font(size=11, weight="bold"),
            text_color=ThemeManager.get_color("text_muted"),
            fg_color=ThemeManager.get_color("bg_active"),
            corner_radius=ThemeManager.CORNER_RADIUS_SM,
            width=180,
            height=26
        )
        self.att_status_lbl.grid(row=3, column=0, columnspan=2, sticky="w", padx=ThemeManager.PAD_MD, pady=ThemeManager.PAD_SM)

        # Action Buttons frame
        self.att_buttons_frame = ctk.CTkFrame(self.attendance_card, fg_color="transparent")
        self.att_buttons_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=ThemeManager.PAD_MD, pady=(ThemeManager.PAD_XS, ThemeManager.PAD_MD))
        self.att_buttons_frame.grid_columnconfigure((0, 1), weight=1)

        self.confirm_att_btn = ctk.CTkButton(
            self.att_buttons_frame,
            text="Confirm Present",
            font=ThemeManager.get_font(size=11, weight="bold"),
            fg_color=ThemeManager.get_color("accent_success"),
            text_color=ThemeManager.get_color("text_dark"),
            hover_color=ThemeManager.get_color("bg_active"),
            state="disabled",
            command=self.confirm_attendance
        )
        self.confirm_att_btn.grid(row=0, column=0, padx=2, sticky="ew")

        self.cancel_att_btn = ctk.CTkButton(
            self.att_buttons_frame,
            text="Cancel",
            font=ThemeManager.get_font(size=11),
            fg_color=ThemeManager.get_color("bg_active"),
            text_color=ThemeManager.get_color("text_primary"),
            hover_color=ThemeManager.get_color("bg_card"),
            state="disabled",
            command=self.cancel_attendance
        )
        self.cancel_att_btn.grid(row=0, column=1, padx=2, sticky="ew")

    def handle_recognition_event(self, res: dict) -> None:
        """
        Coordinates either auto check-in or populating the manual confirm action widgets.
        """
        student_id = res["student_id"]
        
        # 1. Cooldown bypass checks
        if self.attendance_controller.service.is_in_cooldown(student_id):
            self.show_attendance_feedback(res, status_type="already_marked", message="Cooldown period active.")
            return

        # 2. Validation: check configured workflow model
        if not self.recognition_controller.service.settings.attendance_auto_mode:
            # Confirmation mode
            if self.pending_confirmation_student_id is not None:
                return  # Skip processing other frames during pending confirmation
            
            self.pending_confirmation_student_id = student_id
            self.pending_recognition_result = res
            self.show_attendance_feedback(res, status_type="pending_confirmation")
        else:
            # Auto mode
            result = self.attendance_controller.mark_attendance(
                student_id=student_id,
                score=res["distance_or_similarity"],
                method="LBPH"
            )
            if result.success:
                if result.already_marked:
                    self.show_attendance_feedback(res, status_type="already_marked", message="Already marked today.")
                else:
                    self.show_attendance_feedback(res, status_type="success", message=result.status)
            else:
                self.show_attendance_feedback(res, status_type="error", message=result.message)

    def confirm_attendance(self) -> None:
        """
        Triggers database write upon clicking the Confirm Present button.
        """
        if self.pending_recognition_result:
            res = self.pending_recognition_result
            student_id = res["student_id"]
            result = self.attendance_controller.mark_attendance(
                student_id=student_id,
                score=res["distance_or_similarity"],
                method="LBPH"
            )
            if result.success:
                if result.already_marked:
                    self.show_attendance_feedback(res, status_type="already_marked", message="Already marked today.")
                else:
                    self.show_attendance_feedback(res, status_type="success", message=result.status)
            else:
                self.show_attendance_feedback(res, status_type="error", message=result.message)
        self.clear_pending_confirmation()

    def cancel_attendance(self) -> None:
        """
        Aborts the pending confirmation flow.
        """
        self.clear_pending_confirmation()
        self.show_attendance_feedback(None, status_type="idle")

    def clear_pending_confirmation(self) -> None:
        self.pending_confirmation_student_id = None
        self.pending_recognition_result = None

    def show_attendance_feedback(self, res: dict | None, status_type: str, message: str = "") -> None:
        """
        Redraws the details inside the attendance logging card.
        """
        if status_type == "idle" or res is None:
            self.att_student_name_val.configure(text="No detection", text_color=ThemeManager.get_color("text_muted"))
            self.att_student_code_val.configure(text="-", text_color=ThemeManager.get_color("text_muted"))
            self.att_status_lbl.configure(text="STATUS: Idle", text_color=ThemeManager.get_color("text_muted"), fg_color=ThemeManager.get_color("bg_active"))
            self.confirm_att_btn.configure(state="disabled")
            self.cancel_att_btn.configure(state="disabled")
            return

        name = res["student_name"]
        code = res["student_code"]
        score = res["distance_or_similarity"]

        self.att_student_name_val.configure(text=name, text_color=ThemeManager.get_color("text_primary"))
        self.att_student_code_val.configure(text=f"ID: {code} | Match: {score:.2f}", text_color=ThemeManager.get_color("text_light"))

        if status_type == "pending_confirmation":
            self.att_status_lbl.configure(
                text="PENDING CONFIRMATION",
                text_color=ThemeManager.get_color("text_dark"),
                fg_color=ThemeManager.get_color("accent_warning")
            )
            self.confirm_att_btn.configure(state="normal")
            self.cancel_att_btn.configure(state="normal")
        elif status_type == "success":
            self.att_status_lbl.configure(
                text=f"✓ RECORDED ({message})",
                text_color=ThemeManager.get_color("text_dark"),
                fg_color=ThemeManager.get_color("accent_success")
            )
            self.confirm_att_btn.configure(state="disabled")
            self.cancel_att_btn.configure(state="disabled")
        elif status_type == "already_marked":
            self.att_status_lbl.configure(
                text=f"ℹ ALREADY RECORDED ({message})",
                text_color=ThemeManager.get_color("text_dark"),
                fg_color=ThemeManager.get_color("accent_secondary")
            )
            self.confirm_att_btn.configure(state="disabled")
            self.cancel_att_btn.configure(state="disabled")
        elif status_type == "error":
            self.att_status_lbl.configure(
                text=f"⚠ ERROR: {message}",
                text_color=ThemeManager.get_color("text_light"),
                fg_color=ThemeManager.get_color("accent_danger")
            )
            self.confirm_att_btn.configure(state="disabled")
            self.cancel_att_btn.configure(state="disabled")
