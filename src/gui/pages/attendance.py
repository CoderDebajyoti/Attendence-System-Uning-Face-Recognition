# ==============================================================================
# Face Recognition Attendance System - Attendance Tracking Page View
# ==============================================================================

import customtkinter as ctk
from datetime import datetime
from src.gui.themes import ThemeManager
from src.gui.pages.base import BasePage
from src.gui.components import Card, Dialog, MessageBox
from src.controllers.attendance_controller import AttendanceController
from src.utils.time_helper import get_current_date, format_display_time

class AttendancePage(BasePage):
    """
    Attendance Tracking Page View. Renders today's session summary stats,
    search logs, date/department/status filters, and coordinates manual entries and corrections.
    """
    def __init__(self, parent, controller) -> None:
        self.attendance_controller = AttendanceController()
        
        # Keep track of active filters
        self.search_val = ""
        self.selected_date = get_current_date()
        self.selected_status = None
        self.selected_dept_id = None
        self.selected_course_id = None
        self.selected_source = None
        
        super().__init__(
            parent=parent,
            controller=controller,
            title="Attendance Tracking Panel",
            description="Monitor live check-in events, search historical logs, apply filters, and record manual corrections.",
            phase=10
        )

    def show_default_placeholder(self) -> None:
        """
        Overrides the base class placeholder to render the actual Attendance Registry view.
        """
        # Configure layout grids inside content area
        self.content_frame.grid_columnconfigure(0, weight=7)  # Left panel (70% - table & filters)
        self.content_frame.grid_columnconfigure(1, weight=3)  # Right panel (30% - today's session card)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Left Panel layout
        self.left_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.left_container.grid(row=0, column=0, sticky="nsew", padx=(0, ThemeManager.PAD_MD))
        self.left_container.grid_columnconfigure(0, weight=1)
        self.left_container.grid_rowconfigure(1, weight=1)  # Table expands
        
        # 1. Search and Filter Panel (Top left)
        self.create_filter_panel()
        
        # 2. Table Logs Canvas
        self.table_canvas = ctk.CTkFrame(self.left_container, fg_color="transparent")
        self.table_canvas.grid(row=1, column=0, sticky="nsew", pady=(ThemeManager.PAD_MD, 0))
        self.table_canvas.grid_columnconfigure(0, weight=1)
        self.table_canvas.grid_rowconfigure(0, weight=1)

        # Right Panel layout
        self.right_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.right_container.grid(row=0, column=1, sticky="nsew", padx=(ThemeManager.PAD_MD, 0))
        self.right_container.grid_columnconfigure(0, weight=1)
        
        # 3. Today's Session metrics card
        self.create_session_stats_card()
        
        # Initial load
        self.refresh_all()

    def create_filter_panel(self) -> None:
        """
        Renders the search bar and selection dropdowns at the top.
        """
        panel = Card(self.left_container)
        panel.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        panel.grid_columnconfigure((0, 1, 2), weight=1)
        panel.grid_columnconfigure(3, weight=0)

        # Row 0: Search inputs and button
        search_frame = ctk.CTkFrame(panel, fg_color="transparent")
        search_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=ThemeManager.PAD_MD, pady=ThemeManager.PAD_SM)
        
        self.search_entry = ctk.CTkEntry(
            search_frame, 
            placeholder_text="Search by Student ID, Name, Roll No...",
            font=ThemeManager.get_font(size=12),
            height=32
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, ThemeManager.PAD_SM))
        self.search_entry.bind("<Return>", lambda e: self.trigger_search())

        search_btn = ctk.CTkButton(
            search_frame,
            text="Search",
            font=ThemeManager.get_font(size=12, weight="bold"),
            fg_color=ThemeManager.get_color("bg_active"),
            text_color=ThemeManager.get_color("text_primary"),
            hover_color=ThemeManager.get_color("bg_card"),
            width=80,
            height=32,
            command=self.trigger_search
        )
        search_btn.pack(side="left", padx=ThemeManager.PAD_XS)

        # Date input
        date_frame = ctk.CTkFrame(panel, fg_color="transparent")
        date_frame.grid(row=0, column=2, columnspan=2, sticky="ew", padx=ThemeManager.PAD_MD, pady=ThemeManager.PAD_SM)
        
        date_lbl = ctk.CTkLabel(date_frame, text="Date:", font=ThemeManager.get_font(size=11, weight="bold"), text_color=ThemeManager.get_color("text_muted"))
        date_lbl.pack(side="left", padx=(0, 4))
        
        self.date_entry = ctk.CTkEntry(
            date_frame,
            placeholder_text="YYYY-MM-DD",
            font=ThemeManager.get_font(size=12),
            width=120,
            height=32
        )
        self.date_entry.insert(0, self.selected_date)
        self.date_entry.pack(side="left", fill="x", expand=True, padx=(0, ThemeManager.PAD_SM))
        self.date_entry.bind("<Return>", lambda e: self.trigger_search())

        # Row 1: Filters
        depts = self.attendance_controller.get_departments()
        self.dept_options = ["All Departments"] + [d.name for d in depts]
        self.dept_map = {d.name: d.id for d in depts}
        
        self.dept_menu = ctk.CTkOptionMenu(
            panel,
            values=self.dept_options,
            font=ThemeManager.get_font(size=11),
            dropdown_font=ThemeManager.get_font(size=11),
            height=28,
            fg_color=ThemeManager.get_color("bg_active"),
            button_color=ThemeManager.get_color("bg_active"),
            text_color=ThemeManager.get_color("text_primary"),
            command=self.on_department_filter_changed
        )
        self.dept_menu.grid(row=1, column=0, sticky="ew", padx=ThemeManager.PAD_MD, pady=ThemeManager.PAD_SM)

        self.course_menu = ctk.CTkOptionMenu(
            panel,
            values=["All Courses"],
            font=ThemeManager.get_font(size=11),
            dropdown_font=ThemeManager.get_font(size=11),
            height=28,
            fg_color=ThemeManager.get_color("bg_active"),
            button_color=ThemeManager.get_color("bg_active"),
            text_color=ThemeManager.get_color("text_primary"),
            command=self.on_course_filter_changed
        )
        self.course_menu.grid(row=1, column=1, sticky="ew", padx=ThemeManager.PAD_MD, pady=ThemeManager.PAD_SM)
        self.update_course_dropdown()

        self.status_menu = ctk.CTkOptionMenu(
            panel,
            values=["All Statuses", "PRESENT", "LATE", "ABSENT", "EXCUSED"],
            font=ThemeManager.get_font(size=11),
            dropdown_font=ThemeManager.get_font(size=11),
            height=28,
            fg_color=ThemeManager.get_color("bg_active"),
            button_color=ThemeManager.get_color("bg_active"),
            text_color=ThemeManager.get_color("text_primary"),
            command=self.on_status_filter_changed
        )
        self.status_menu.grid(row=1, column=2, sticky="ew", padx=ThemeManager.PAD_MD, pady=ThemeManager.PAD_SM)

        # Source menu filter
        self.source_menu = ctk.CTkOptionMenu(
            panel,
            values=["All Sources", "FACE_RECOGNITION", "MANUAL"],
            font=ThemeManager.get_font(size=11),
            dropdown_font=ThemeManager.get_font(size=11),
            height=28,
            fg_color=ThemeManager.get_color("bg_active"),
            button_color=ThemeManager.get_color("bg_active"),
            text_color=ThemeManager.get_color("text_primary"),
            command=self.on_source_filter_changed
        )
        self.source_menu.grid(row=1, column=3, sticky="ew", padx=ThemeManager.PAD_MD, pady=ThemeManager.PAD_SM)

    def update_course_dropdown(self) -> None:
        courses = self.attendance_controller.get_courses(self.selected_dept_id)
        self.course_options = ["All Courses"] + [c.name for c in courses]
        self.course_map = {c.name: c.id for c in courses}
        self.course_menu.configure(values=self.course_options)
        self.course_menu.set("All Courses")
        self.selected_course_id = None

    def trigger_search(self) -> None:
        self.search_val = self.search_entry.get().strip()
        self.selected_date = self.date_entry.get().strip() or None
        self.refresh_table_list()

    def on_department_filter_changed(self, value: str) -> None:
        self.selected_dept_id = self.dept_map.get(value)
        self.update_course_dropdown()
        self.refresh_table_list()

    def on_course_filter_changed(self, value: str) -> None:
        self.selected_course_id = self.course_map.get(value)
        self.refresh_table_list()

    def on_status_filter_changed(self, value: str) -> None:
        self.selected_status = None if value == "All Statuses" else value
        self.refresh_table_list()

    def on_source_filter_changed(self, value: str) -> None:
        self.selected_source = None if value == "All Sources" else value
        self.refresh_table_list()

    def create_session_stats_card(self) -> None:
        """
        Renders the right-side summary card with stats and action triggers.
        """
        self.stats_card = Card(self.right_container)
        self.stats_card.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.stats_card.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(
            self.stats_card,
            text="Today's Session Stats",
            font=ThemeManager.get_font(size=14, weight="bold"),
            text_color=ThemeManager.get_color("accent_primary")
        )
        title.grid(row=0, column=0, columnspan=2, sticky="w", padx=ThemeManager.PAD_LG, pady=ThemeManager.PAD_LG)

        self.stats_labels = {}
        rows = [
            ("Date Tracker", "-"),
            ("Active Session", "-"),
            ("Total Marked", "0"),
            ("Present Today", "0"),
            ("Late Today", "0"),
            ("Unmarked Students", "0"),
            ("Attendance Rate", "0.0%")
        ]

        for idx, (label_name, default_val) in enumerate(rows):
            lbl_key = ctk.CTkLabel(
                self.stats_card,
                text=f"{label_name}:",
                font=ThemeManager.get_font(size=12, weight="bold"),
                text_color=ThemeManager.get_color("text_muted")
            )
            lbl_key.grid(row=idx+1, column=0, sticky="w", padx=ThemeManager.PAD_LG, pady=6)

            lbl_val = ctk.CTkLabel(
                self.stats_card,
                text=default_val,
                font=ThemeManager.get_font(size=12, weight="bold" if idx >= 2 else "normal"),
                text_color=ThemeManager.get_color("text_primary")
            )
            lbl_val.grid(row=idx+1, column=1, sticky="w", padx=ThemeManager.PAD_LG, pady=6)
            self.stats_labels[label_name] = lbl_val

        # Highlight attendance rate
        self.stats_labels["Attendance Rate"].configure(text_color=ThemeManager.get_color("accent_success"))

        # Manual Log button
        self.manual_btn = ctk.CTkButton(
            self.stats_card,
            text="Mark Attendance Manually",
            font=ThemeManager.get_font(size=12, weight="bold"),
            fg_color=ThemeManager.get_color("accent_primary"),
            text_color=ThemeManager.get_color("text_dark"),
            hover_color=ThemeManager.get_color("bg_active"),
            height=36,
            command=self.open_manual_dialog
        )
        self.manual_btn.grid(row=8, column=0, columnspan=2, sticky="ew", padx=ThemeManager.PAD_LG, pady=ThemeManager.PAD_LG)

        # Refresh button
        self.refresh_btn = ctk.CTkButton(
            self.stats_card,
            text="Refresh Board",
            font=ThemeManager.get_font(size=11),
            fg_color="transparent",
            border_color=ThemeManager.get_color("border"),
            border_width=1,
            text_color=ThemeManager.get_color("text_light"),
            hover_color=ThemeManager.get_color("bg_active"),
            height=28,
            command=self.refresh_all
        )
        self.refresh_btn.grid(row=9, column=0, columnspan=2, sticky="ew", padx=ThemeManager.PAD_LG, pady=(0, ThemeManager.PAD_LG))

    def refresh_all(self) -> None:
        self.refresh_stats()
        self.refresh_table_list()

    def refresh_stats(self) -> None:
        """
        Calculates today's stats from the DB and displays in right stats panel.
        """
        stats = self.attendance_controller.get_today_statistics()
        
        self.stats_labels["Date Tracker"].configure(text=get_current_date())
        self.stats_labels["Active Session"].configure(text=stats["session_name"])
        self.stats_labels["Total Marked"].configure(text=str(stats["total_marked"]))
        self.stats_labels["Present Today"].configure(text=str(stats["present"]))
        self.stats_labels["Late Today"].configure(text=str(stats["late"]))
        self.stats_labels["Unmarked Students"].configure(text=str(stats["not_marked"]))
        self.stats_labels["Attendance Rate"].configure(text=f"{stats['rate']}%")

        # Dynamically update the app status bar and dashboard metrics if accessible
        app = self.controller
        if hasattr(app, "initialize_status_metrics"):
            app.initialize_status_metrics()


    def refresh_table_list(self) -> None:
        """
        Wipes table content canvas and queries matching logs.
        """
        for w in self.table_canvas.winfo_children():
            w.destroy()

        records = self.attendance_controller.get_filtered_attendance(
            search_query=self.search_val,
            date_str=self.selected_date,
            status=self.selected_status,
            department_id=self.selected_dept_id,
            course_id=self.selected_course_id,
            source=self.selected_source
        )

        if not records:
            self.render_empty_state()
        else:
            self.render_attendance_table(records)

    def render_empty_state(self) -> None:
        card = Card(self.table_canvas)
        card.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)

        panel = ctk.CTkFrame(card, fg_color="transparent")
        panel.grid(row=0, column=0)

        icon = ctk.CTkLabel(panel, text="📝", font=ThemeManager.get_font(size=48))
        icon.pack(pady=10)

        lbl = ctk.CTkLabel(
            panel,
            text="No Attendance Records Found",
            font=ThemeManager.get_font(size=14, weight="bold"),
            text_color=ThemeManager.get_color("text_primary")
        )
        lbl.pack(pady=5)

        lbl2 = ctk.CTkLabel(
            panel,
            text="Change the date or filters, or mark attendance manually.",
            font=ThemeManager.get_font(size=11),
            text_color=ThemeManager.get_color("text_muted")
        )
        lbl2.pack(pady=5)

    def render_attendance_table(self, records: list) -> None:
        container = Card(self.table_canvas)
        container.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)

        # 1. Table Header
        header = ctk.CTkFrame(container, fg_color=ThemeManager.get_color("bg_active"), height=36, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)

        columns = [
            ("ID", 0.08),
            ("Student ID", 0.14),
            ("Student Name", 0.22),
            ("Time", 0.12),
            ("Status", 0.12),
            ("Match Score", 0.12),
            ("Source", 0.12),
            ("Actions", 0.08)
        ]

        curr_relx = 0.01
        for col_name, col_width in columns:
            lbl = ctk.CTkLabel(
                header,
                text=col_name,
                font=ThemeManager.get_font(size=11, weight="bold"),
                text_color=ThemeManager.get_color("text_primary")
            )
            lbl.place(relx=curr_relx, rely=0.5, relwidth=col_width-0.01, anchor="w")
            curr_relx += col_width

        # 2. Scrollable Rows Area
        scroll_area = ctk.CTkScrollableFrame(container, fg_color="transparent", corner_radius=0)
        scroll_area.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
        scroll_area.grid_columnconfigure(0, weight=1)

        for idx, rec in enumerate(records):
            row = ctk.CTkFrame(
                scroll_area,
                height=40,
                fg_color="transparent" if idx % 2 == 0 else ThemeManager.get_color("bg_main"),
                corner_radius=4
            )
            row.grid(row=idx, column=0, sticky="ew", pady=1)
            row.grid_propagate(False)

            status_colors = {
                "PRESENT": ThemeManager.get_color("accent_success"),
                "LATE": ThemeManager.get_color("accent_warning"),
                "ABSENT": ThemeManager.get_color("accent_danger"),
                "EXCUSED": ThemeManager.get_color("accent_secondary")
            }
            status_color = status_colors.get(rec.status, ThemeManager.get_color("text_primary"))

            score_val = f"{rec.recognition_score:.2f}" if rec.recognition_score else "-"
            source_txt = rec.source

            # Populate fields
            values = [
                (str(rec.id), 0.08, ThemeManager.get_color("text_muted")),
                (rec.student.student_code, 0.14, ThemeManager.get_color("text_primary")),
                (f"{rec.student.first_name} {rec.student.last_name}", 0.22, ThemeManager.get_color("text_primary")),
                (format_display_time(rec.time_in), 0.12, ThemeManager.get_color("text_light")),
                (rec.status, 0.12, status_color),
                (score_val, 0.12, ThemeManager.get_color("text_muted")),
                (source_txt, 0.12, ThemeManager.get_color("text_muted"))
            ]

            curr_relx = 0.01
            for text_val, width, color in values:
                lbl = ctk.CTkLabel(
                    row,
                    text=text_val,
                    font=ThemeManager.get_font(size=11),
                    text_color=color,
                    anchor="w"
                )
                lbl.place(relx=curr_relx, rely=0.5, relwidth=width-0.01, anchor="w")
                curr_relx += width

            # Actions buttons frame
            btn_frame = ctk.CTkFrame(row, fg_color="transparent")
            btn_frame.place(relx=curr_relx, rely=0.5, relwidth=0.08, relheight=0.8, anchor="w")

            # Edit status button
            e_btn = ctk.CTkButton(
                btn_frame, text="✏️", font=ThemeManager.get_font(size=10),
                fg_color="transparent", width=22, hover_color=ThemeManager.get_color("bg_active"),
                text_color=ThemeManager.get_color("accent_primary"),
                command=lambda r_id=rec.id: self.open_edit_dialog(r_id)
            )
            e_btn.pack(side="left", padx=1)

            # Deletion button
            d_btn = ctk.CTkButton(
                btn_frame, text="🗑️", font=ThemeManager.get_font(size=10),
                fg_color="transparent", width=22, hover_color=ThemeManager.get_color("bg_active"),
                text_color=ThemeManager.get_color("accent_danger"),
                command=lambda r_id=rec.id: self.confirm_delete_record(r_id)
            )
            d_btn.pack(side="left", padx=1)

    def open_manual_dialog(self) -> None:
        dialog = ManualAttendanceDialog(self, controller=self.attendance_controller)
        self.wait_window(dialog)
        self.refresh_all()

    def open_edit_dialog(self, record_id: int) -> None:
        dialog = EditAttendanceDialog(self, record_id=record_id, controller=self.attendance_controller)
        self.wait_window(dialog)
        self.refresh_all()

    def confirm_delete_record(self, record_id: int) -> None:
        rec = self.attendance_controller.service.repo.get_record_by_id(record_id)
        if not rec:
            return

        msg = (
            f"Are you sure you want to delete the attendance record for:\n"
            f"{rec.student.first_name} {rec.student.last_name} ({rec.student.student_code}) on {rec.date}?\n\n"
            f"Note: Deletion cannot be undone."
        )

        confirm = MessageBox(self, title="Confirm Deletion", message=msg, icon_type="warning", show_cancel=True)
        self.wait_window(confirm)

        if confirm.result:
            success = self.attendance_controller.delete_attendance(record_id)
            if success:
                alert = MessageBox(self, title="Success", message="Record deleted successfully.", icon_type="success")
                self.wait_window(alert)
                self.refresh_all()
            else:
                alert = MessageBox(self, title="Error", message="Could not complete deletion.", icon_type="error")
                self.wait_window(alert)


class ManualAttendanceDialog(Dialog):
    """
    Form dialog to record manual student check-ins.
    """
    def __init__(self, parent, controller: AttendanceController) -> None:
        self.controller = controller
        super().__init__(parent, "Log Manual Attendance", width=460, height=360)
        self.build_form()

    def build_form(self) -> None:
        # Fetch active students list
        students = self.controller.list_students(status="Active")
        self.student_options = [f"{s.first_name} {s.last_name} ({s.student_code})" for s in students]
        self.student_map = {f"{s.first_name} {s.last_name} ({s.student_code})": s.id for s in students}

        # Student Dropdown Selection
        row1 = ctk.CTkFrame(self.container, fg_color="transparent")
        row1.pack(fill="x", pady=6)
        lbl1 = ctk.CTkLabel(row1, text="Select Student*", font=ThemeManager.get_font(size=11, weight="bold"), text_color=ThemeManager.get_color("text_light"))
        lbl1.pack(anchor="w")

        self.student_menu = ctk.CTkOptionMenu(
            row1,
            values=self.student_options,
            font=ThemeManager.get_font(size=11),
            dropdown_font=ThemeManager.get_font(size=11),
            height=28,
            fg_color=ThemeManager.get_color("bg_active"),
            button_color=ThemeManager.get_color("bg_active"),
            text_color=ThemeManager.get_color("text_primary")
        )
        self.student_menu.pack(fill="x", pady=2)

        # Date Entry
        row2 = ctk.CTkFrame(self.container, fg_color="transparent")
        row2.pack(fill="x", pady=6)
        lbl2 = ctk.CTkLabel(row2, text="Date (YYYY-MM-DD)*", font=ThemeManager.get_font(size=11, weight="bold"), text_color=ThemeManager.get_color("text_light"))
        lbl2.pack(anchor="w")
        
        self.date_input = ctk.CTkEntry(row2, font=ThemeManager.get_font(size=11), height=28)
        self.date_input.insert(0, get_current_date())
        self.date_input.pack(fill="x", pady=2)

        # Status Option
        row3 = ctk.CTkFrame(self.container, fg_color="transparent")
        row3.pack(fill="x", pady=6)
        lbl3 = ctk.CTkLabel(row3, text="Attendance Status*", font=ThemeManager.get_font(size=11, weight="bold"), text_color=ThemeManager.get_color("text_light"))
        lbl3.pack(anchor="w")

        self.status_menu = ctk.CTkOptionMenu(
            row3,
            values=["PRESENT", "LATE", "ABSENT", "EXCUSED"],
            font=ThemeManager.get_font(size=11),
            dropdown_font=ThemeManager.get_font(size=11),
            height=28,
            fg_color=ThemeManager.get_color("bg_active"),
            button_color=ThemeManager.get_color("bg_active"),
            text_color=ThemeManager.get_color("text_primary")
        )
        self.status_menu.pack(fill="x", pady=2)

        # Reason Reason field
        row4 = ctk.CTkFrame(self.container, fg_color="transparent")
        row4.pack(fill="x", pady=6)
        lbl4 = ctk.CTkLabel(row4, text="Reason / Note*", font=ThemeManager.get_font(size=11, weight="bold"), text_color=ThemeManager.get_color("text_light"))
        lbl4.pack(anchor="w")

        self.reason_input = ctk.CTkEntry(row4, placeholder_text="e.g. Medical emergency, biometric system bypass", font=ThemeManager.get_font(size=11), height=28)
        self.reason_input.pack(fill="x", pady=2)

        # Action Buttons
        btn_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(ThemeManager.PAD_MD, 0))

        save_btn = ctk.CTkButton(
            btn_frame,
            text="Save Record",
            font=ThemeManager.get_font(size=12, weight="bold"),
            fg_color=ThemeManager.get_color("accent_primary"),
            text_color=ThemeManager.get_color("text_dark"),
            hover_color=ThemeManager.get_color("bg_active"),
            width=100,
            command=self.submit
        )
        save_btn.pack(side="right", padx=ThemeManager.PAD_XS)

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            font=ThemeManager.get_font(size=12),
            fg_color="transparent",
            border_color=ThemeManager.get_color("border"),
            border_width=1,
            text_color=ThemeManager.get_color("text_light"),
            hover_color=ThemeManager.get_color("bg_active"),
            width=80,
            command=self.destroy
        )
        cancel_btn.pack(side="right", padx=ThemeManager.PAD_XS)

    def submit(self) -> None:
        sel_student = self.student_menu.get()
        student_id = self.student_map.get(sel_student)
        date_str = self.date_input.get().strip()
        status_val = self.status_menu.get()
        reason_txt = self.reason_input.get().strip()

        if not student_id:
            MessageBox(self, title="Error", message="Please select a valid student.", icon_type="error")
            return

        if not date_str or not reason_txt:
            MessageBox(self, title="Error", message="Date and Reason notes are required fields.", icon_type="error")
            return

        try:
            # Format validation
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            MessageBox(self, title="Error", message="Date must follow YYYY-MM-DD format.", icon_type="error")
            return

        result = self.controller.mark_attendance_manual(
            student_id=student_id,
            date_str=date_str,
            status=status_val,
            reason=reason_txt,
            marked_by="Admin Manual Override"
        )

        if result.success:
            if result.already_marked:
                MessageBox(self, title="Info", message="Attendance record already exists for this student on this date.", icon_type="info")
            else:
                MessageBox(self, title="Success", message="Manual attendance recorded successfully.", icon_type="success")
            self.destroy()
        else:
            MessageBox(self, title="Transaction Failure", message=result.message, icon_type="error")


class EditAttendanceDialog(Dialog):
    """
    Form dialog to modify/correct an existing attendance record status.
    """
    def __init__(self, parent, record_id: int, controller: AttendanceController) -> None:
        self.controller = controller
        self.record_id = record_id
        super().__init__(parent, "Correct Attendance Status", width=420, height=220)
        self.build_form()

    def build_form(self) -> None:
        rec = self.controller.service.repo.get_record_by_id(self.record_id)
        if not rec:
            self.destroy()
            return

        self.student_name_label = ctk.CTkLabel(
            self.container,
            text=f"Correcting: {rec.student.first_name} {rec.student.last_name} ({rec.student.student_code})",
            font=ThemeManager.get_font(size=12, weight="bold"),
            text_color=ThemeManager.get_color("text_primary"),
            anchor="w"
        )
        self.student_name_label.pack(fill="x", pady=4)

        # Status Option
        row1 = ctk.CTkFrame(self.container, fg_color="transparent")
        row1.pack(fill="x", pady=6)
        lbl1 = ctk.CTkLabel(row1, text="Select Corrected Status*", font=ThemeManager.get_font(size=11, weight="bold"), text_color=ThemeManager.get_color("text_light"))
        lbl1.pack(anchor="w")

        self.status_menu = ctk.CTkOptionMenu(
            row1,
            values=["PRESENT", "LATE", "ABSENT", "EXCUSED"],
            font=ThemeManager.get_font(size=11),
            dropdown_font=ThemeManager.get_font(size=11),
            height=28,
            fg_color=ThemeManager.get_color("bg_active"),
            button_color=ThemeManager.get_color("bg_active"),
            text_color=ThemeManager.get_color("text_primary")
        )
        self.status_menu.set(rec.status)
        self.status_menu.pack(fill="x", pady=2)

        # Actions buttons
        btn_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(ThemeManager.PAD_MD, 0))

        save_btn = ctk.CTkButton(
            btn_frame,
            text="Apply Correction",
            font=ThemeManager.get_font(size=12, weight="bold"),
            fg_color=ThemeManager.get_color("accent_primary"),
            text_color=ThemeManager.get_color("text_dark"),
            hover_color=ThemeManager.get_color("bg_active"),
            width=120,
            command=self.submit
        )
        save_btn.pack(side="right", padx=ThemeManager.PAD_XS)

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            font=ThemeManager.get_font(size=12),
            fg_color="transparent",
            border_color=ThemeManager.get_color("border"),
            border_width=1,
            text_color=ThemeManager.get_color("text_light"),
            hover_color=ThemeManager.get_color("bg_active"),
            width=80,
            command=self.destroy
        )
        cancel_btn.pack(side="right", padx=ThemeManager.PAD_XS)

    def submit(self) -> None:
        status_val = self.status_menu.get()
        success, message = self.controller.update_attendance(
            record_id=self.record_id,
            status=status_val,
            updated_by="Admin Manual Edit Override"
        )

        if success:
            MessageBox(self, title="Success", message=message, icon_type="success")
            self.destroy()
        else:
            MessageBox(self, title="Error", message=message, icon_type="error")
