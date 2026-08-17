# ==============================================================================
# Face Recognition Attendance System - System Settings Page View
# ==============================================================================

import customtkinter as ctk
import logging
from pathlib import Path
from src.gui.pages.base import BasePage
from src.gui.themes import ThemeManager
from src.gui.components import Card, MessageBox

logger = logging.getLogger("app.gui")

class SettingsPage(BasePage):
    """
    System Settings configuration view. Provides input fields to manage and save
    environment configurations, confidence metrics, camera IDs, and folder paths.
    """
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            title="System Configurations",
            description="Configure environment variables, recognition confidence metrics, secret keys, and database connections.",
            phase=1
        )

    def show_default_placeholder(self) -> None:
        """
        Overrides base placeholder to render the configurations form.
        """
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Form scroll container
        self.scroll_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        self.scroll_frame.grid(row=0, column=0, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        # Form Card Wrapper
        self.form_card = Card(self.scroll_frame)
        self.form_card.pack(fill="x", padx=10, pady=10)
        self.form_card.grid_columnconfigure(1, weight=1)

        settings = self.controller.settings

        # 1. Section Header: Biometrics
        self.add_section_header("Biometric Model Settings", 0)
        
        # Recognition threshold
        self.threshold_entry = self.add_form_row("Recognition Threshold (LBPH)", "Range: 0.0 - 1.0 (Higher is more strict)", str(settings.recognition_threshold), 1)
        
        # Target image count
        self.target_count_entry = self.add_form_row("Target Biometric Images Count", "Number of template crops to capture", str(settings.target_image_count), 2)

        # Cooldown minutes
        self.cooldown_entry = self.add_form_row("Attendance Cooldown (Minutes)", "Ignore duplicate check-ins within this period", str(settings.cooldown_minutes), 3)

        # 2. Section Header: Camera Streams
        self.add_section_header("Camera Interface Configuration", 4)

        # Camera ID
        self.camera_id_entry = self.add_form_row("Camera ID (Local Devices)", "Index (0 for default default webcam, 1, 2, etc.)", str(settings.camera_id), 5)

        # Camera RTSP URL
        self.rtsp_entry = self.add_form_row("Camera RTSP Stream Link", "Alternative RTSP network stream URL", settings.camera_rtsp_url, 6)

        # Camera test connection button
        test_btn = ctk.CTkButton(
            self.form_card,
            text="Test Camera Stream Feed",
            font=ThemeManager.get_font(size=11, weight="bold"),
            fg_color=ThemeManager.get_color("bg_active"),
            text_color=ThemeManager.get_color("text_primary"),
            hover_color=ThemeManager.get_color("bg_card"),
            height=28,
            command=self.test_camera_connection
        )
        test_btn.grid(row=7, column=1, sticky="w", padx=ThemeManager.PAD_LG, pady=ThemeManager.PAD_SM)

        # 3. Section Header: Directory Structures
        self.add_section_header("Storage Folders Mappings", 8)

        # Model storage path
        self.model_path_entry = self.add_form_row("Model Metadata Folder", "Target folder for recognition_model.xml", str(settings.model_path), 9)

        # Dataset storage path
        self.dataset_path_entry = self.add_form_row("Biometric Datasets Folder", "Target directory for face cropped samples", str(settings.dataset_path), 10)

        # Export path
        self.export_path_entry = self.add_form_row("Reports Exports Folder", "Target folder for generated CSV and Excel spreadsheets", str(settings.export_path), 11)

        # 4. Section Header: Developer Log Levels
        self.add_section_header("Diagnostics Log Priority", 12)

        # Log Level
        lbl_log = ctk.CTkLabel(self.form_card, text="System Log Level", font=ThemeManager.get_font(size=12, weight="bold"), text_color=ThemeManager.get_color("text_light"))
        lbl_log.grid(row=13, column=0, sticky="w", padx=ThemeManager.PAD_LG, pady=ThemeManager.PAD_SM)
        
        self.log_level_menu = ctk.CTkOptionMenu(
            self.form_card,
            values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            font=ThemeManager.get_font(size=12),
            dropdown_font=ThemeManager.get_font(size=12),
            fg_color=ThemeManager.get_color("bg_active"),
            button_color=ThemeManager.get_color("bg_active"),
            text_color=ThemeManager.get_color("text_primary")
        )
        self.log_level_menu.grid(row=13, column=1, sticky="w", padx=ThemeManager.PAD_LG, pady=ThemeManager.PAD_SM)
        self.log_level_menu.set(settings.log_level)

        # 5. Form Actions footer
        action_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=10, pady=(15, 30))

        self.status_lbl = ctk.CTkLabel(
            action_frame,
            text="",
            font=ThemeManager.get_font(size=12, weight="bold"),
            text_color=ThemeManager.get_color("accent_success")
        )
        self.status_lbl.pack(side="left", padx=10)

        save_btn = ctk.CTkButton(
            action_frame,
            text="Save Configurations",
            font=ThemeManager.get_font(size=12, weight="bold"),
            fg_color=ThemeManager.get_color("accent_primary"),
            text_color=ThemeManager.get_color("text_dark"),
            hover_color=ThemeManager.get_color("bg_active"),
            height=34,
            command=self.save_settings
        )
        save_btn.pack(side="right")

    def add_section_header(self, text: str, row: int) -> None:
        lbl = ctk.CTkLabel(
            self.form_card,
            text=text,
            font=ThemeManager.get_font(size=13, weight="bold"),
            text_color=ThemeManager.get_color("accent_primary")
        )
        lbl.grid(row=row, column=0, columnspan=2, sticky="w", padx=ThemeManager.PAD_LG, pady=(ThemeManager.PAD_MD, ThemeManager.PAD_XS))

    def add_form_row(self, label_text: str, description_text: str, initial_value: str, row: int) -> ctk.CTkEntry:
        lbl_frame = ctk.CTkFrame(self.form_card, fg_color="transparent")
        lbl_frame.grid(row=row, column=0, sticky="w", padx=ThemeManager.PAD_LG, pady=ThemeManager.PAD_SM)
        
        title = ctk.CTkLabel(lbl_frame, text=label_text, font=ThemeManager.get_font(size=12, weight="bold"), text_color=ThemeManager.get_color("text_light"))
        title.pack(anchor="w")
        
        desc = ctk.CTkLabel(lbl_frame, text=description_text, font=ThemeManager.get_font(size=10), text_color=ThemeManager.get_color("text_muted"))
        desc.pack(anchor="w")
        
        entry = ctk.CTkEntry(
            self.form_card,
            font=ThemeManager.get_font(size=12),
            height=30
        )
        entry.grid(row=row, column=1, sticky="ew", padx=ThemeManager.PAD_LG, pady=ThemeManager.PAD_SM)
        entry.insert(0, initial_value)
        
        return entry

    def save_settings(self) -> None:
        self.status_lbl.configure(text="")
        
        # 1. Capture inputs
        threshold_raw = self.threshold_entry.get().strip()
        target_count_raw = self.target_count_entry.get().strip()
        cooldown_raw = self.cooldown_entry.get().strip()
        camera_id_raw = self.camera_id_entry.get().strip()
        rtsp_url = self.rtsp_entry.get().strip()
        model_path = self.model_path_entry.get().strip()
        dataset_path = self.dataset_path_entry.get().strip()
        export_path = self.export_path_entry.get().strip()
        log_level = self.log_level_menu.get()

        # 2. Validation
        try:
            threshold = float(threshold_raw)
            if not (0.0 <= threshold <= 1.0):
                raise ValueError()
        except ValueError:
            self.show_error("Confidence threshold must be a float value between 0.0 and 1.0.")
            return

        try:
            target_count = int(target_count_raw)
            if target_count <= 0:
                raise ValueError()
        except ValueError:
            self.show_error("Target template count must be a positive integer.")
            return

        try:
            cooldown = int(cooldown_raw)
            if cooldown < 0:
                raise ValueError()
        except ValueError:
            self.show_error("Cooldown minutes must be a non-negative integer.")
            return

        try:
            camera_id = int(camera_id_raw)
            if camera_id < 0:
                raise ValueError()
        except ValueError:
            self.show_error("Camera ID must be a non-negative integer.")
            return

        if not model_path or not dataset_path or not export_path:
            self.show_error("Storage folder path values cannot be empty.")
            return

        # 3. Update settings runtime object
        settings = self.controller.settings
        settings.recognition_threshold = threshold
        settings.target_image_count = target_count
        settings.cooldown_minutes = cooldown
        settings.camera_id = camera_id
        settings.camera_rtsp_url = rtsp_url
        settings.model_path = Path(model_path)
        settings.dataset_path = Path(dataset_path)
        settings.export_path = Path(export_path)
        settings.log_level = log_level

        # Re-initialize logging framework if log level changes
        logging.getLogger().setLevel(log_level)

        # 4. Save to local .env file
        self.persist_to_env(settings)

        self.status_lbl.configure(text="✓ Configurations saved and applied successfully.", text_color=ThemeManager.get_color("accent_success"))

    def persist_to_env(self, settings) -> None:
        """
        Parses and updates the local .env configuration key-value storage.
        """
        env_path = Path(".env")
        lines = []
        if env_path.exists():
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            except Exception as e:
                logger.error(f"Failed to read .env file: {e}")

        # Map current variables
        vars_dict = {}
        for line in lines:
            clean = line.strip()
            if "=" in clean and not clean.startswith("#"):
                k, v = clean.split("=", 1)
                vars_dict[k.strip()] = v.strip()

        # Update dict keys
        vars_dict["RECOGNITION_THRESHOLD"] = f'"{settings.recognition_threshold}"'
        vars_dict["TARGET_IMAGE_COUNT"] = f'"{settings.target_image_count}"'
        vars_dict["COOLDOWN_MINUTES"] = f'"{settings.cooldown_minutes}"'
        vars_dict["CAMERA_ID"] = f'"{settings.camera_id}"'
        vars_dict["CAMERA_RTSP_URL"] = f'"{settings.camera_rtsp_url}"'
        vars_dict["MODEL_PATH"] = f'"{settings.model_path}"'
        vars_dict["DATASET_PATH"] = f'"{settings.dataset_path}"'
        vars_dict["EXPORT_PATH"] = f'"{settings.export_path}"'
        vars_dict["LOG_LEVEL"] = f'"{settings.log_level}"'

        try:
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("# ==============================================================================\n")
                f.write("# Face Recognition Attendance System - Configuration Settings (Auto-Generated)\n")
                f.write("# ==============================================================================\n")
                for k, v in vars_dict.items():
                    f.write(f"{k}={v}\n")
            logger.info("Local configuration .env variables persisted successfully.")
        except Exception as e:
            logger.error(f"Failed to write settings to .env: {e}")

    def show_error(self, message: str) -> None:
        self.status_lbl.configure(text=f"✗ {message}", text_color=ThemeManager.get_color("accent_danger"))

    def test_camera_connection(self) -> None:
        """
        Spawns a popup window with a live stream viewer to test the configured Camera ID or RTSP URL.
        """
        source = 0
        camera_id_raw = self.camera_id_entry.get().strip()
        rtsp_url = self.rtsp_entry.get().strip()
        
        if rtsp_url:
            source = rtsp_url
        else:
            try:
                source = int(camera_id_raw)
            except ValueError:
                self.show_error("Camera ID must be an integer index.")
                return

        # Spawn top-level window
        test_win = ctk.CTkToplevel(self)
        test_win.title("Camera Connection Test Viewfinder")
        test_win.geometry("500x440")
        test_win.resizable(False, False)
        test_win.transient(self)
        test_win.grab_set()
        
        # Center inside this page
        self.controller.update_idletasks()
        x = self.controller.winfo_x() + (self.controller.winfo_width() - 500) // 2
        y = self.controller.winfo_y() + (self.controller.winfo_height() - 440) // 2
        test_win.geometry(f"500x440+{x}+{y}")
        
        test_win.configure(fg_color=ThemeManager.get_color("bg_main"))
        
        lbl = ctk.CTkLabel(
            test_win, 
            text=f"Testing Camera Source: {source}", 
            font=ThemeManager.get_font(size=13, weight="bold"),
            text_color=ThemeManager.get_color("text_primary")
        )
        lbl.pack(pady=10)
        
        canvas = ctk.CTkLabel(
            test_win,
            text="Camera stream loading...",
            fg_color=ThemeManager.get_color("bg_active"),
            width=400,
            height=300
        )
        canvas.pack(padx=20, pady=10)
        
        # Start stream thread
        from src.gui.pages.dataset import CameraReader
        from PIL import Image
        
        reader = CameraReader(source)
        reader.start()
        
        active = [True]
        
        def update_frame():
            if not active[0]:
                return
            if reader.error_occurred:
                canvas.configure(text=f"Error: {reader.error_message}", text_color=ThemeManager.get_color("accent_danger"))
                return
            frame = reader.latest_frame
            if frame is not None:
                try:
                    import cv2
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_img = Image.fromarray(rgb)
                    pil_img = pil_img.resize((400, 300), Image.Resampling.LANCZOS)
                    ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(400, 300))
                    canvas.configure(image=ctk_img, text="")
                except Exception as e:
                    logger.error(f"Error drawing preview frame: {e}")
            test_win.after(33, update_frame)
            
        test_win.after(100, update_frame)
        
        def close_test():
            active[0] = False
            reader.stop()
            test_win.destroy()
            
        test_win.protocol("WM_DELETE_WINDOW", close_test)
        
        close_btn = ctk.CTkButton(
            test_win,
            text="Close Test Viewfinder",
            font=ThemeManager.get_font(size=12, weight="bold"),
            fg_color=ThemeManager.get_color("bg_active"),
            text_color=ThemeManager.get_color("text_primary"),
            command=close_test
        )
        close_btn.pack(pady=10)
