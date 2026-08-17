# ==============================================================================
# Face Recognition Attendance System - Dataset Page View
# ==============================================================================

import customtkinter as ctk
import cv2
import threading
import time
import os
import logging
from PIL import Image
from pathlib import Path
from src.gui.pages.base import BasePage
from src.gui.themes import ThemeManager
from src.gui.components import Card, MessageBox
from src.controllers import DatasetController
from src.core import constants

logger = logging.getLogger("app.gui")

class CameraReader(threading.Thread):
    """
    Background worker thread to read camera frames continuously
    to prevent blocking the CustomTkinter UI event loop.
    """
    def __init__(self, source) -> None:
        super().__init__()
        self.source = source
        self.running = False
        self.cap = None
        self.latest_frame = None
        self.error_occurred = False
        self.error_message = ""

    def run(self) -> None:
        self.running = True
        try:
            logger.info(f"Opening camera source: {self.source}")
            self.cap = cv2.VideoCapture(self.source)
            # Set default resolution limits for compatibility
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            if not self.cap.isOpened():
                self.error_occurred = True
                self.error_message = "Camera unavailable or already in use."
                self.running = False
                return

            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    self.error_occurred = True
                    self.error_message = "Camera stream disconnected."
                    break
                self.latest_frame = frame
                # Limit frame acquisition overhead (~30 FPS)
                time.sleep(0.03)
        except Exception as e:
            self.error_occurred = True
            self.error_message = f"Camera initialization failure: {e}"
            logger.exception("Error in CameraReader thread:")
        finally:
            if self.cap:
                self.cap.release()
            self.running = False

    def stop(self) -> None:
        self.running = False
        self.join(timeout=1.0)


class DatasetPage(BasePage):
    """
    Dataset Management Page View. Implements Phase 8 Face Dataset Collection & Validation.
    Includes student dropdown selection, camera live feed with face detection box,
    captured crop gallery, validation diagnostics, and directory clearing.
    """
    def __init__(self, parent, controller) -> None:
        self.dataset_controller = DatasetController()
        self.selected_student = None
        self.camera_reader = None
        self.update_loop_id = None
        self.is_camera_active = False

        super().__init__(
            parent=parent,
            controller=controller,
            title="Biometric Dataset Manager",
            description="Acquire face training samples, track alignment coordinates, and audit dataset compliance.",
            phase=8
        )

    def show_default_placeholder(self) -> None:
        """
        Overrides the base coming-soon placeholder to draw the full Dataset Manager UI.
        """
        # Configure layout grids inside content area
        self.content_frame.grid_columnconfigure(0, weight=4)  # Left controls & stats (40%)
        self.content_frame.grid_columnconfigure(1, weight=6)  # Right camera & preview (60%)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # 1. Left Side Panel Container
        self.left_panel = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, ThemeManager.PAD_MD))
        self.left_panel.grid_columnconfigure(0, weight=1)
        self.left_panel.grid_rowconfigure(2, weight=1)

        # Left Column Card 1: Student Selection
        self.create_selection_card()

        # Left Column Card 2: Student Details & Dataset Status
        self.create_status_card()

        # Left Column Card 3: Dataset Validation Diagnostic checklist
        self.create_validation_card()

        # 2. Right Side Panel Container
        self.right_panel = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(ThemeManager.PAD_MD, 0))
        self.right_panel.grid_columnconfigure(0, weight=1)
        self.right_panel.grid_rowconfigure(1, weight=1)

        # Right Column Card 1: Camera Live Preview Frame
        self.create_camera_card()

        # Right Column Card 2: Thumbnail Gallery
        self.create_gallery_card()

        # Bind tab visibility change check to stop camera when navigating away
        self.check_visibility()

    def check_visibility(self) -> None:
        """
        Periodically checks if the page is active/visible. Stops the camera if hidden.
        """
        if not self.winfo_ismapped() and self.is_camera_active:
            logger.info("DatasetPage hidden. Automatically stopping camera stream.")
            self.stop_camera()
        self.after(1000, self.check_visibility)

    def create_selection_card(self) -> None:
        card = Card(self.left_panel)
        card.grid(row=0, column=0, sticky="ew", pady=(0, ThemeManager.PAD_SM))
        card.grid_columnconfigure(0, weight=1)

        lbl = ctk.CTkLabel(
            card,
            text="Student Selection",
            font=ThemeManager.get_font(size=12, weight="bold"),
            text_color=ThemeManager.get_color("accent_primary")
        )
        lbl.grid(row=0, column=0, sticky="w", padx=ThemeManager.PAD_MD, pady=(ThemeManager.PAD_SM, ThemeManager.PAD_XS))

        # Fetch active students list
        self.students = self.dataset_controller.get_active_students()
        self.student_options = ["Select a Student"] + [
            f"{s.first_name} {s.last_name} ({s.student_code})" for s in self.students
        ]
        self.student_map = {
            f"{s.first_name} {s.last_name} ({s.student_code})": s.id for s in self.students
        }

        self.student_menu = ctk.CTkOptionMenu(
            card,
            values=self.student_options,
            font=ThemeManager.get_font(size=12),
            dropdown_font=ThemeManager.get_font(size=12),
            fg_color=ThemeManager.get_color("bg_active"),
            button_color=ThemeManager.get_color("bg_active"),
            text_color=ThemeManager.get_color("text_primary"),
            command=self.on_student_selected
        )
        self.student_menu.grid(row=1, column=0, sticky="ew", padx=ThemeManager.PAD_MD, pady=(0, ThemeManager.PAD_SM))

    def create_status_card(self) -> None:
        self.status_card = Card(self.left_panel)
        self.status_card.grid(row=1, column=0, sticky="ew", pady=ThemeManager.PAD_SM)
        self.status_card.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(
            self.status_card,
            text="Student Profile & Dataset Status",
            font=ThemeManager.get_font(size=12, weight="bold"),
            text_color=ThemeManager.get_color("accent_primary")
        )
        title.grid(row=0, column=0, columnspan=2, sticky="w", padx=ThemeManager.PAD_MD, pady=(ThemeManager.PAD_SM, ThemeManager.PAD_XS))

        # Text labels mapping
        self.labels = {}
        info_rows = [
            ("Name", "-"),
            ("Student ID", "-"),
            ("Department", "-"),
            ("Course", "-"),
            ("Enrollment Status", "-"),
            ("Dataset Status", "-"),
            ("Captured Count", "-"),
            ("Recognition Profile", "-")
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
            self.labels[label_name] = lbl_val

    def create_validation_card(self) -> None:
        self.val_card = Card(self.left_panel)
        self.val_card.grid(row=2, column=0, sticky="nsew", pady=(ThemeManager.PAD_SM, 0))
        self.val_card.grid_columnconfigure(1, weight=1)
        self.val_card.grid_rowconfigure(6, weight=1)

        title = ctk.CTkLabel(
            self.val_card,
            text="Biometric Audit & Validation",
            font=ThemeManager.get_font(size=12, weight="bold"),
            text_color=ThemeManager.get_color("accent_primary")
        )
        title.grid(row=0, column=0, columnspan=2, sticky="w", padx=ThemeManager.PAD_MD, pady=(ThemeManager.PAD_SM, ThemeManager.PAD_XS))

        self.checklist_labels = {}
        checks = [
            ("Directory Structure", "Not validated"),
            ("Minimum Image Count", "Not validated"),
            ("Image Readability", "Not validated"),
            ("Face Align Dimension", "Not validated"),
            ("Single Face Presence", "Not validated")
        ]

        for idx, (check_name, default_status) in enumerate(checks):
            lbl_check = ctk.CTkLabel(
                self.val_card,
                text=check_name,
                font=ThemeManager.get_font(size=11, weight="bold"),
                text_color=ThemeManager.get_color("text_muted")
            )
            lbl_check.grid(row=idx+1, column=0, sticky="w", padx=ThemeManager.PAD_MD, pady=3)

            lbl_stat = ctk.CTkLabel(
                self.val_card,
                text=default_status,
                font=ThemeManager.get_font(size=11),
                text_color=ThemeManager.get_color("text_muted")
            )
            lbl_stat.grid(row=idx+1, column=1, sticky="w", padx=ThemeManager.PAD_MD, pady=3)
            self.checklist_labels[check_name] = lbl_stat

        # Validation Action Button
        self.validate_btn = ctk.CTkButton(
            self.val_card,
            text="Validate Dataset",
            font=ThemeManager.get_font(size=12, weight="bold"),
            fg_color=ThemeManager.get_color("accent_secondary"),
            text_color=ThemeManager.get_color("text_dark"),
            hover_color=ThemeManager.get_color("bg_active"),
            state="disabled",
            command=self.run_manual_validation
        )
        self.validate_btn.grid(row=7, column=0, columnspan=2, sticky="ew", padx=ThemeManager.PAD_MD, pady=ThemeManager.PAD_SM)

        # Clear Dataset Action Button
        self.clear_btn = ctk.CTkButton(
            self.val_card,
            text="Clear Dataset",
            font=ThemeManager.get_font(size=12, weight="bold"),
            fg_color="transparent",
            border_color=ThemeManager.get_color("accent_danger"),
            border_width=1,
            text_color=ThemeManager.get_color("accent_danger"),
            hover_color=ThemeManager.get_color("bg_active"),
            state="disabled",
            command=self.confirm_clear_dataset
        )
        self.clear_btn.grid(row=8, column=0, columnspan=2, sticky="ew", padx=ThemeManager.PAD_MD, pady=(0, ThemeManager.PAD_MD))

    def create_camera_card(self) -> None:
        self.cam_card = Card(self.right_panel)
        self.cam_card.grid(row=0, column=0, sticky="nsew", pady=(0, ThemeManager.PAD_SM))
        self.cam_card.grid_columnconfigure(0, weight=1)
        self.cam_card.grid_rowconfigure(1, weight=1)

        # Header Title
        title = ctk.CTkLabel(
            self.cam_card,
            text="Live Camera Preview",
            font=ThemeManager.get_font(size=12, weight="bold"),
            text_color=ThemeManager.get_color("accent_primary")
        )
        title.grid(row=0, column=0, sticky="w", padx=ThemeManager.PAD_MD, pady=(ThemeManager.PAD_SM, 2))

        # Preview viewport area
        self.preview_frame = ctk.CTkFrame(self.cam_card, fg_color="#11111b", height=300)
        self.preview_frame.grid(row=1, column=0, sticky="nsew", padx=ThemeManager.PAD_MD, pady=ThemeManager.PAD_XS)
        self.preview_frame.grid_propagate(False)
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame.grid_rowconfigure(0, weight=1)

        self.preview_lbl = ctk.CTkLabel(
            self.preview_frame,
            text="Select a student and click [Start Camera]",
            font=ThemeManager.get_font(size=13, slant="italic"),
            text_color=ThemeManager.get_color("text_muted")
        )
        self.preview_lbl.grid(row=0, column=0)

        # Status overlay info label
        self.feed_status_lbl = ctk.CTkLabel(
            self.cam_card,
            text="Stream: Offline",
            font=ThemeManager.get_font(size=11),
            text_color=ThemeManager.get_color("text_muted")
        )
        self.feed_status_lbl.grid(row=2, column=0, sticky="w", padx=ThemeManager.PAD_MD, pady=2)

        # Camera Controls Panel
        self.controls_frame = ctk.CTkFrame(self.cam_card, fg_color="transparent")
        self.controls_frame.grid(row=3, column=0, sticky="ew", padx=ThemeManager.PAD_MD, pady=ThemeManager.PAD_SM)
        self.controls_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.start_btn = ctk.CTkButton(
            self.controls_frame,
            text="Start Camera",
            font=ThemeManager.get_font(size=12, weight="bold"),
            fg_color=ThemeManager.get_color("accent_success"),
            text_color=ThemeManager.get_color("text_dark"),
            state="disabled",
            command=self.start_camera
        )
        self.start_btn.grid(row=0, column=0, padx=2)

        self.capture_btn = ctk.CTkButton(
            self.controls_frame,
            text="Capture Image",
            font=ThemeManager.get_font(size=12, weight="bold"),
            fg_color=ThemeManager.get_color("accent_primary"),
            text_color=ThemeManager.get_color("text_dark"),
            state="disabled",
            command=self.trigger_capture
        )
        self.capture_btn.grid(row=0, column=1, padx=2)

        self.stop_btn = ctk.CTkButton(
            self.controls_frame,
            text="Stop Camera",
            font=ThemeManager.get_font(size=12, weight="bold"),
            fg_color=ThemeManager.get_color("bg_active"),
            text_color=ThemeManager.get_color("text_primary"),
            state="disabled",
            command=self.stop_camera
        )
        self.stop_btn.grid(row=0, column=2, padx=2)

        self.finish_btn = ctk.CTkButton(
            self.controls_frame,
            text="Finish",
            font=ThemeManager.get_font(size=12, weight="bold"),
            fg_color=ThemeManager.get_color("accent_secondary"),
            text_color=ThemeManager.get_color("text_dark"),
            state="disabled",
            command=self.finish_dataset
        )
        self.finish_btn.grid(row=0, column=3, padx=2)

    def create_gallery_card(self) -> None:
        self.gallery_card = Card(self.right_panel)
        self.gallery_card.grid(row=1, column=0, sticky="nsew", pady=(ThemeManager.PAD_SM, 0))
        self.gallery_card.grid_columnconfigure(0, weight=1)
        self.gallery_card.grid_rowconfigure(1, weight=1)

        title = ctk.CTkLabel(
            self.gallery_card,
            text="Dataset Thumbnail Gallery",
            font=ThemeManager.get_font(size=12, weight="bold"),
            text_color=ThemeManager.get_color("accent_primary")
        )
        title.grid(row=0, column=0, sticky="w", padx=ThemeManager.PAD_MD, pady=(ThemeManager.PAD_SM, 2))

        # Horizontal Scroll Area
        self.gallery_scroll = ctk.CTkScrollableFrame(self.gallery_card, height=130, orientation="horizontal", fg_color="transparent")
        self.gallery_scroll.grid(row=1, column=0, sticky="nsew", padx=ThemeManager.PAD_MD, pady=(0, ThemeManager.PAD_MD))
        self.gallery_scroll.grid_rowconfigure(0, weight=1)

        # Re-render empty state by default
        self.refresh_gallery_views()

    def select_student_by_id(self, student_id: int) -> None:
        """
        External setter to programmatic update selected student index.
        Invoked during redirects from the StudentsDetails dialog.
        """
        for opt_str, s_id in self.student_map.items():
            if s_id == student_id:
                self.student_menu.set(opt_str)
                self.on_student_selected(opt_str)
                break

    def on_student_selected(self, option_str: str) -> None:
        """
        Callback handler when dropdown updates. Sets local records context.
        """
        # Close camera if active
        if self.is_camera_active:
            self.stop_camera()

        self.selected_student_id = self.student_map.get(option_str)

        if not self.selected_student_id:
            self.selected_student = None
            self.reset_ui_labels()
            self.disable_all_controls()
            return

        # Load Student details
        self.selected_student = self.dataset_controller.get_student_details(self.selected_student_id)
        if not self.selected_student:
            self.reset_ui_labels()
            self.disable_all_controls()
            return

        self.update_ui_with_selected_student()
        self.enable_student_controls()
        self.refresh_gallery_views()
        self.reset_validation_display()

    def reset_ui_labels(self) -> None:
        for label_name in self.labels:
            self.labels[label_name].configure(text="-")
        self.feed_status_lbl.configure(text="Stream: Offline")

    def disable_all_controls(self) -> None:
        self.start_btn.configure(state="disabled")
        self.capture_btn.configure(state="disabled")
        self.stop_btn.configure(state="disabled")
        self.finish_btn.configure(state="disabled")
        self.validate_btn.configure(state="disabled")
        self.clear_btn.configure(state="disabled")

    def enable_student_controls(self) -> None:
        self.start_btn.configure(state="normal")
        self.validate_btn.configure(state="normal")
        self.clear_btn.configure(state="normal")

    def update_ui_with_selected_student(self) -> None:
        student = self.selected_student
        dataset = self.dataset_controller.get_dataset_details(student.id)

        self.labels["Name"].configure(text=f"{student.first_name} {student.last_name}")
        self.labels["Student ID"].configure(text=student.student_code)
        self.labels["Department"].configure(text=student.department.name)
        self.labels["Course"].configure(text=student.course.name)
        self.labels["Enrollment Status"].configure(text=student.status)

        # Format dataset status values with colors
        status_colors = {
            "READY": ThemeManager.get_color("accent_success"),
            "COLLECTING": ThemeManager.get_color("accent_warning"),
            "NEEDS_UPDATE": ThemeManager.get_color("accent_warning"),
            "INVALID": ThemeManager.get_color("accent_danger"),
            "NOT_REGISTERED": ThemeManager.get_color("accent_danger")
        }
        status_str = dataset.status if dataset else "NOT_REGISTERED"
        color = status_colors.get(status_str, ThemeManager.get_color("text_primary"))
        self.labels["Dataset Status"].configure(text=status_str, text_color=color)

        img_count = dataset.image_count if dataset else 0
        target = self.dataset_controller.get_target_image_count()
        self.labels["Captured Count"].configure(text=f"{img_count} / {target}")

        # Check recognition profile status
        try:
            from src.services.face_recognition_service import FaceRecognitionService
            rec_service = FaceRecognitionService.get_instance()
            is_in_model = rec_service.is_student_in_model(student.id)
            is_outdated = rec_service.is_model_outdated()
            
            if is_in_model:
                if is_outdated:
                    rec_profile_str = "Model Update Required"
                    rec_profile_color = ThemeManager.get_color("accent_warning")
                else:
                    rec_profile_str = "Included in Model"
                    rec_profile_color = ThemeManager.get_color("accent_success")
            else:
                if dataset and dataset.status == "READY":
                    rec_profile_str = "Model Update Required"
                    rec_profile_color = ThemeManager.get_color("accent_warning")
                else:
                    rec_profile_str = "Not Registered"
                    rec_profile_color = ThemeManager.get_color("text_muted")
        except Exception:
            rec_profile_str = "Not Registered"
            rec_profile_color = ThemeManager.get_color("text_muted")
            
        self.labels["Recognition Profile"].configure(text=rec_profile_str, text_color=rec_profile_color)

    def reset_validation_display(self) -> None:
        for val_lbl in self.checklist_labels.values():
            val_lbl.configure(text="Not validated", text_color=ThemeManager.get_color("text_muted"))

    def start_camera(self) -> None:
        """
        Attempts to initialize cv2 capture streams on background thread.
        """
        if not self.selected_student:
            return

        # Resolve cam index from settings
        settings = self.dataset_controller.service.settings
        cam_source = settings.camera_rtsp_url if settings.camera_rtsp_url else settings.camera_id

        self.feed_status_lbl.configure(text="Initialising camera...", text_color=ThemeManager.get_color("accent_warning"))
        
        self.camera_reader = CameraReader(cam_source)
        self.camera_reader.start()

        # Schedule check inside UI thread
        self.after(500, self.check_camera_startup)

    def check_camera_startup(self) -> None:
        if not self.camera_reader:
            return

        if self.camera_reader.error_occurred:
            msg = self.camera_reader.error_message
            self.stop_camera()
            alert = MessageBox(self, title="Camera Error", message=msg, icon_type="error")
            self.wait_window(alert)
            self.feed_status_lbl.configure(text="Offline (Error)", text_color=ThemeManager.get_color("accent_danger"))
            return

        if self.camera_reader.running:
            self.is_camera_active = True
            self.feed_status_lbl.configure(text="Stream: Active (Live)", text_color=ThemeManager.get_color("accent_success"))
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.capture_btn.configure(state="normal")
            self.finish_btn.configure(state="normal")
            
            # Start UI feed loop
            self.preview_lbl.configure(text="")
            self.update_camera_frame_loop()
        else:
            # Not started yet, retry once
            self.after(200, self.check_camera_startup)

    def update_camera_frame_loop(self) -> None:
        """
        Main loop pulling latest frame from background worker, running overlay detections,
        and rendering to CTkLabel.
        """
        if not self.is_camera_active or not self.camera_reader:
            return

        frame = self.camera_reader.latest_frame
        if frame is not None:
            try:
                # Clone for overlays
                display_frame = frame.copy()
                
                # Fetch detector instance to locate bounding boxes
                detector = self.dataset_controller.service.face_detector
                boxes = detector.detect_faces(display_frame)

                # Draw Bounding Box overlays
                color = (0, 0, 255)  # Red BGR by default
                status_text = "No face detected"

                if len(boxes) == 1:
                    x, y, w, h = boxes[0]
                    # Check centering and size to set green box
                    is_valid, _, _ = detector.validate_face_for_dataset(display_frame)
                    if is_valid:
                        color = (0, 255, 0)  # Green BGR
                        status_text = "Single Face Aligned (Capture Available)"
                    else:
                        color = (0, 200, 255)  # Orange BGR
                        status_text = "Face detected (Adjust alignment)"

                    cv2.rectangle(display_frame, (x, y), (x + w, y + h), color, 2)
                    # Center marker
                    cv2.circle(display_frame, (x + w // 2, y + h // 2), 4, color, -1)
                elif len(boxes) > 1:
                    for x, y, w, h in boxes:
                        cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    status_text = f"Multiple faces ({len(boxes)}) - Ensure only one person is visible"

                # Draw UI Text info overlay
                cv2.putText(display_frame, status_text, (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)

                # Convert to PIL CTkImage format
                rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                # Resize frame to fit viewport
                h_target = 300
                w_target = 400
                pil_img = Image.fromarray(rgb_frame)
                pil_img = pil_img.resize((w_target, h_target), Image.Resampling.LANCZOS)
                
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(w_target, h_target))
                self.preview_lbl.configure(image=ctk_img, text="")
            except Exception as e:
                logger.error(f"Error rendering preview frame: {e}")

        # Schedule next update frame
        self.update_loop_id = self.after(33, self.update_camera_frame_loop)

    def stop_camera(self) -> None:
        """
        Signals stop flag to camera reader thread and releases components.
        """
        self.is_camera_active = False

        if self.update_loop_id:
            self.after_cancel(self.update_loop_id)
            self.update_loop_id = None

        if self.camera_reader:
            self.camera_reader.stop()
            self.camera_reader = None

        self.preview_lbl.configure(image=None, text="Camera Stream Stopped")
        self.feed_status_lbl.configure(text="Stream: Offline", text_color=ThemeManager.get_color("text_muted"))
        
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.capture_btn.configure(state="disabled")
        self.finish_btn.configure(state="disabled")

    def trigger_capture(self) -> None:
        """
        Captures the raw frame from camera reader and saves it to dataset crop paths.
        """
        if not self.is_camera_active or not self.camera_reader:
            return

        frame = self.camera_reader.latest_frame
        if frame is None:
            alert = MessageBox(self, title="Capture Error", message="No frame captured. Please check camera feed.", icon_type="error")
            self.wait_window(alert)
            return

        # Perform service registration check
        success, msg, data = self.dataset_controller.capture_image(self.selected_student_id, frame)
        
        if success:
            logger.info(f"Image saved successfully: {msg}")
            # Refresh stats, thumbnails, and reset validation check status
            self.update_ui_with_selected_student()
            self.refresh_gallery_views()
            self.reset_validation_display()
        else:
            # Show error prompt explaining reject criteria (centering, brightness, count)
            alert = MessageBox(self, title="Validation Reject", message=msg, icon_type="warning")
            self.wait_window(alert)

    def finish_dataset(self) -> None:
        """
        Callback handler to stop the camera and automatically run audit tests.
        """
        self.stop_camera()
        self.run_manual_validation()

    def refresh_gallery_views(self) -> None:
        """
        Rebuilds horizontal previews list on the scroll area.
        """
        # Clear existing children
        for widget in self.gallery_scroll.winfo_children():
            widget.destroy()

        if not self.selected_student:
            empty_lbl = ctk.CTkLabel(self.gallery_scroll, text="Select a student to view gallery", font=ThemeManager.get_font(size=11, slant="italic"), text_color=ThemeManager.get_color("text_muted"))
            empty_lbl.pack(pady=40)
            return

        dataset = self.dataset_controller.get_dataset_details(self.selected_student_id)
        if not dataset or not dataset.images:
            empty_lbl = ctk.CTkLabel(self.gallery_scroll, text="No images captured yet. Start camera to begin.", font=ThemeManager.get_font(size=11, slant="italic"), text_color=ThemeManager.get_color("text_muted"))
            empty_lbl.pack(pady=40)
            return

        # Add image items
        for img in dataset.images:
            img_path = Path(img.file_path)
            if not img_path.exists():
                continue

            # Load thumbnail crop frame
            try:
                pil_img = Image.open(img_path)
                # Resize crop for thumbnail strip
                pil_img = pil_img.resize((70, 70), Image.Resampling.LANCZOS)
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(70, 70))
                
                # Render inside small card frame
                item_frame = ctk.CTkFrame(self.gallery_scroll, fg_color=ThemeManager.get_color("bg_active"), width=80, height=110, corner_radius=ThemeManager.CORNER_RADIUS_SM)
                item_frame.pack(side="left", padx=ThemeManager.PAD_XS)
                item_frame.pack_propagate(False)

                img_lbl = ctk.CTkLabel(item_frame, image=ctk_img, text="")
                img_lbl.pack(pady=(4, 2))

                # mini delete button
                del_btn = ctk.CTkButton(
                    item_frame,
                    text="Delete",
                    font=ThemeManager.get_font(size=9, weight="bold"),
                    fg_color="transparent",
                    text_color=ThemeManager.get_color("accent_danger"),
                    hover_color=ThemeManager.get_color("bg_card"),
                    height=18,
                    width=60,
                    command=lambda i_id=img.id: self.confirm_delete_image(i_id)
                )
                del_btn.pack(pady=2)
            except Exception as e:
                logger.error(f"Failed to load image thumbnail {img_path}: {e}")

    def confirm_delete_image(self, image_id: int) -> None:
        """
        Confirmation window guard before deleting an image.
        """
        confirm = MessageBox(self, title="Delete Image", message="Are you sure you want to delete this dataset image?", icon_type="warning", show_cancel=True)
        self.wait_window(confirm)
        if confirm.result:
            success = self.dataset_controller.delete_image(self.selected_student_id, image_id)
            if success:
                self.update_ui_with_selected_student()
                self.refresh_gallery_views()
                self.reset_validation_display()
            else:
                alert = MessageBox(self, title="Error", message="Could not complete deletion.", icon_type="error")
                self.wait_window(alert)

    def confirm_clear_dataset(self) -> None:
        """
        Double check confirmation before wiping the entire folder.
        """
        msg = f"WARNING: You are about to permanently delete all facial image samples for student: {self.selected_student.first_name} {self.selected_student.last_name}.\n\nThis action cannot be undone."
        confirm = MessageBox(self, title="Wipe Biometric Dataset", message=msg, icon_type="warning", show_cancel=True)
        self.wait_window(confirm)
        if confirm.result:
            # Wipe files and database rows
            success = self.dataset_controller.clear_dataset(self.selected_student_id)
            if success:
                self.update_ui_with_selected_student()
                self.refresh_gallery_views()
                self.reset_validation_display()
                alert = MessageBox(self, title="Dataset Cleared", message="All face images have been removed successfully.", icon_type="success")
                self.wait_window(alert)
            else:
                alert = MessageBox(self, title="Error", message="Failed to clear dataset.", icon_type="error")
                self.wait_window(alert)

    def run_manual_validation(self) -> None:
        """
        Invokes validation checklist service and updates checks markers.
        """
        if not self.selected_student:
            return

        res = self.dataset_controller.validate_dataset(self.selected_student_id)
        
        # Parse and display checkmark indicators
        def format_check_label(lbl, keyword: str, success_msg: str):
            # Check if any error in checklist matches keyword
            matching_errs = [e for e in res["errors"] if keyword.lower() in e.lower()]
            if matching_errs:
                lbl.configure(text="✗ Failed", text_color=ThemeManager.get_color("accent_danger"))
            else:
                lbl.configure(text="✓ Passed", text_color=ThemeManager.get_color("accent_success"))

        # Update labels list
        format_check_label(self.checklist_labels["Directory Structure"], "directory", "Directory exists.")
        format_check_label(self.checklist_labels["Minimum Image Count"], "insufficient", "Minimum images met.")
        format_check_label(self.checklist_labels["Image Readability"], "readable", "Images readable.")
        format_check_label(self.checklist_labels["Face Align Dimension"], "dimension", "Dimensions valid.")
        format_check_label(self.checklist_labels["Single Face Presence"], "exactly one face", "Faces singular check.")

        # Re-sync profile status display colors
        self.update_ui_with_selected_student()

        # Display outcome alert
        if res["success"]:
            msg = f"Verification check completed successfully!\nStatus is now READY. {res['validation_result']}"
            alert = MessageBox(self, title="Validation Success", message=msg, icon_type="success")
            self.wait_window(alert)
        else:
            msg = f"Dataset validation failed checklist audits:\n\n{res['validation_result']}"
            alert = MessageBox(self, title="Validation Failed", message=msg, icon_type="warning")
            self.wait_window(alert)
            
        # Update dashboard status bar metrics
        app = self.controller
        if hasattr(app, "initialize_status_metrics"):
            app.initialize_status_metrics()

    def destroy(self) -> None:
        """
        Overridden window close hook to release camera stream resources.
        """
        self.stop_camera()
        super().destroy()
