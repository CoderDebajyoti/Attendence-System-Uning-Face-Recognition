# ==============================================================================
# Face Recognition Attendance System - Reports & Analytics Page View
# ==============================================================================

import customtkinter as ctk
from datetime import datetime, timedelta
from src.gui.themes import ThemeManager
from src.gui.pages.base import BasePage
from src.gui.components import Card, MessageBox
from src.controllers.reports_controller import ReportsController
from src.utils.time_helper import get_current_date, get_local_now, format_display_time

class ReportsPage(BasePage):
    """
    Reports Page View. Integrates Period/Custom Date Range forms, Department/Course/Status
    dropdown filters, and outputs dynamic tabular report previews and CSV/Excel exports.
    """
    def __init__(self, parent, controller) -> None:
        self.reports_controller = ReportsController()
        
        # State variables
        self.active_report_data = None
        
        super().__init__(
            parent=parent,
            controller=controller,
            title="Reports & Statistical Analytics",
            description="Generate date-range reports, analyze student or course attendance percentages, and export CSV/Excel sheets.",
            phase=11
        )

    def show_default_placeholder(self) -> None:
        """
        Overrides placeholder to render the actual Reports Page layout.
        """
        # Configure layout grids inside the content area
        self.content_frame.grid_columnconfigure(0, weight=3)  # Left panel (30% - filters)
        self.content_frame.grid_columnconfigure(1, weight=7)  # Right panel (70% - summary & preview)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Left Container
        self.left_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.left_container.grid(row=0, column=0, sticky="nsew", padx=(0, ThemeManager.PAD_MD))
        self.left_container.grid_columnconfigure(0, weight=1)
        self.left_container.grid_rowconfigure(0, weight=1)

        # Right Container
        self.right_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.right_container.grid(row=0, column=1, sticky="nsew", padx=(ThemeManager.PAD_MD, 0))
        self.right_container.grid_columnconfigure(0, weight=1)
        self.right_container.grid_rowconfigure(1, weight=1)  # Preview Table expands

        # Build individual panels
        self.create_filters_card()
        self.create_summary_card()
        self.create_preview_panel()

    def create_filters_card(self) -> None:
        """
        Builds the left-side parameters selection card.
        """
        card = Card(self.left_container)
        card.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        card.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            card,
            text="Filter Criteria",
            font=ThemeManager.get_font(size=14, weight="bold"),
            text_color=ThemeManager.get_color("accent_primary")
        )
        title.pack(anchor="w", padx=ThemeManager.PAD_LG, pady=ThemeManager.PAD_MD)

        # 1. Period Option Menu
        lbl_period = ctk.CTkLabel(card, text="Period Selector", font=ThemeManager.get_font(size=11, weight="bold"), text_color=ThemeManager.get_color("text_light"))
        lbl_period.pack(anchor="w", padx=ThemeManager.PAD_LG, pady=(6, 2))
        
        self.period_menu = ctk.CTkOptionMenu(
            card,
            values=["Today", "Yesterday", "This Week", "This Month", "Custom Range"],
            font=ThemeManager.get_font(size=11),
            dropdown_font=ThemeManager.get_font(size=11),
            height=28,
            fg_color=ThemeManager.get_color("bg_active"),
            button_color=ThemeManager.get_color("bg_active"),
            text_color=ThemeManager.get_color("text_primary"),
            command=self.on_period_changed
        )
        self.period_menu.pack(fill="x", padx=ThemeManager.PAD_LG, pady=2)
        self.period_menu.set("Today")

        # 2. Custom Date Range Entries
        self.date_range_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.date_range_frame.pack(fill="x", padx=ThemeManager.PAD_LG, pady=4)
        self.date_range_frame.grid_columnconfigure((0, 1), weight=1)

        lbl_start = ctk.CTkLabel(self.date_range_frame, text="Start Date", font=ThemeManager.get_font(size=10, weight="bold"), text_color=ThemeManager.get_color("text_muted"))
        lbl_start.grid(row=0, column=0, sticky="w", padx=2)
        self.start_date_entry = ctk.CTkEntry(self.date_range_frame, placeholder_text="YYYY-MM-DD", font=ThemeManager.get_font(size=11), height=28, state="disabled")
        self.start_date_entry.grid(row=1, column=0, sticky="ew", padx=2, pady=2)

        lbl_end = ctk.CTkLabel(self.date_range_frame, text="End Date", font=ThemeManager.get_font(size=10, weight="bold"), text_color=ThemeManager.get_color("text_muted"))
        lbl_end.grid(row=0, column=1, sticky="w", padx=2)
        self.end_date_entry = ctk.CTkEntry(self.date_range_frame, placeholder_text="YYYY-MM-DD", font=ThemeManager.get_font(size=11), height=28, state="disabled")
        self.end_date_entry.grid(row=1, column=1, sticky="ew", padx=2, pady=2)

        self.set_preset_dates("Today")

        # 3. Student Filter
        students = self.reports_controller.list_students()
        self.student_options = ["All Students"] + [f"{s.first_name} {s.last_name} ({s.student_code})" for s in students]
        self.student_map = {f"{s.first_name} {s.last_name} ({s.student_code})": s.id for s in students}
        
        lbl_student = ctk.CTkLabel(card, text="Filter Student", font=ThemeManager.get_font(size=11, weight="bold"), text_color=ThemeManager.get_color("text_light"))
        lbl_student.pack(anchor="w", padx=ThemeManager.PAD_LG, pady=(6, 2))
        
        self.student_menu = ctk.CTkOptionMenu(
            card,
            values=self.student_options,
            font=ThemeManager.get_font(size=11),
            dropdown_font=ThemeManager.get_font(size=11),
            height=28,
            fg_color=ThemeManager.get_color("bg_active"),
            button_color=ThemeManager.get_color("bg_active"),
            text_color=ThemeManager.get_color("text_primary")
        )
        self.student_menu.pack(fill="x", padx=ThemeManager.PAD_LG, pady=2)

        # 4. Department & Course Filters
        depts = self.reports_controller.get_departments()
        self.dept_options = ["All Departments"] + [d.name for d in depts]
        self.dept_map = {d.name: d.id for d in depts}

        lbl_dept = ctk.CTkLabel(card, text="Filter Department", font=ThemeManager.get_font(size=11, weight="bold"), text_color=ThemeManager.get_color("text_light"))
        lbl_dept.pack(anchor="w", padx=ThemeManager.PAD_LG, pady=(6, 2))

        self.dept_menu = ctk.CTkOptionMenu(
            card,
            values=self.dept_options,
            font=ThemeManager.get_font(size=11),
            dropdown_font=ThemeManager.get_font(size=11),
            height=28,
            fg_color=ThemeManager.get_color("bg_active"),
            button_color=ThemeManager.get_color("bg_active"),
            text_color=ThemeManager.get_color("text_primary"),
            command=self.on_department_changed
        )
        self.dept_menu.pack(fill="x", padx=ThemeManager.PAD_LG, pady=2)

        lbl_course = ctk.CTkLabel(card, text="Filter Course", font=ThemeManager.get_font(size=11, weight="bold"), text_color=ThemeManager.get_color("text_light"))
        lbl_course.pack(anchor="w", padx=ThemeManager.PAD_LG, pady=(6, 2))

        self.course_menu = ctk.CTkOptionMenu(
            card,
            values=["All Courses"],
            font=ThemeManager.get_font(size=11),
            dropdown_font=ThemeManager.get_font(size=11),
            height=28,
            fg_color=ThemeManager.get_color("bg_active"),
            button_color=ThemeManager.get_color("bg_active"),
            text_color=ThemeManager.get_color("text_primary")
        )
        self.course_menu.pack(fill="x", padx=ThemeManager.PAD_LG, pady=2)
        self.update_course_dropdown()

        # 5. Status & Source Filters
        lbl_status = ctk.CTkLabel(card, text="Filter Status", font=ThemeManager.get_font(size=11, weight="bold"), text_color=ThemeManager.get_color("text_light"))
        lbl_status.pack(anchor="w", padx=ThemeManager.PAD_LG, pady=(6, 2))

        self.status_menu = ctk.CTkOptionMenu(
            card,
            values=["All Statuses", "PRESENT", "LATE", "ABSENT", "EXCUSED"],
            font=ThemeManager.get_font(size=11),
            dropdown_font=ThemeManager.get_font(size=11),
            height=28,
            fg_color=ThemeManager.get_color("bg_active"),
            button_color=ThemeManager.get_color("bg_active"),
            text_color=ThemeManager.get_color("text_primary")
        )
        self.status_menu.pack(fill="x", padx=ThemeManager.PAD_LG, pady=2)

        lbl_source = ctk.CTkLabel(card, text="Filter Source", font=ThemeManager.get_font(size=11, weight="bold"), text_color=ThemeManager.get_color("text_light"))
        lbl_source.pack(anchor="w", padx=ThemeManager.PAD_LG, pady=(6, 2))

        self.source_menu = ctk.CTkOptionMenu(
            card,
            values=["All Sources", "FACE_RECOGNITION", "MANUAL"],
            font=ThemeManager.get_font(size=11),
            dropdown_font=ThemeManager.get_font(size=11),
            height=28,
            fg_color=ThemeManager.get_color("bg_active"),
            button_color=ThemeManager.get_color("bg_active"),
            text_color=ThemeManager.get_color("text_primary")
        )
        self.source_menu.pack(fill="x", padx=ThemeManager.PAD_LG, pady=2)

        # 6. Action Triggers
        self.generate_btn = ctk.CTkButton(
            card,
            text="Generate Report",
            font=ThemeManager.get_font(size=12, weight="bold"),
            fg_color=ThemeManager.get_color("accent_primary"),
            text_color=ThemeManager.get_color("text_dark"),
            hover_color=ThemeManager.get_color("bg_active"),
            height=34,
            command=self.trigger_generate_report
        )
        self.generate_btn.pack(fill="x", padx=ThemeManager.PAD_LG, pady=(15, 6))

        self.export_csv_btn = ctk.CTkButton(
            card,
            text="Export CSV",
            font=ThemeManager.get_font(size=11),
            fg_color="transparent",
            border_color=ThemeManager.get_color("border"),
            border_width=1,
            text_color=ThemeManager.get_color("text_light"),
            hover_color=ThemeManager.get_color("bg_active"),
            state="disabled",
            height=28,
            command=self.trigger_export_csv
        )
        self.export_csv_btn.pack(fill="x", padx=ThemeManager.PAD_LG, pady=2)

        self.export_excel_btn = ctk.CTkButton(
            card,
            text="Export Excel",
            font=ThemeManager.get_font(size=11),
            fg_color="transparent",
            border_color=ThemeManager.get_color("border"),
            border_width=1,
            text_color=ThemeManager.get_color("text_light"),
            hover_color=ThemeManager.get_color("bg_active"),
            state="disabled",
            height=28,
            command=self.trigger_export_excel
        )
        self.export_excel_btn.pack(fill="x", padx=ThemeManager.PAD_LG, pady=(2, ThemeManager.PAD_LG))

    def on_period_changed(self, value: str) -> None:
        if value == "Custom Range":
            self.start_date_entry.configure(state="normal")
            self.end_date_entry.configure(state="normal")
        else:
            self.start_date_entry.configure(state="normal")
            self.end_date_entry.configure(state="normal")
            self.set_preset_dates(value)
            self.start_date_entry.configure(state="disabled")
            self.end_date_entry.configure(state="disabled")

    def set_preset_dates(self, preset: str) -> None:
        self.start_date_entry.delete(0, "end")
        self.end_date_entry.delete(0, "end")
        
        now = get_local_now()
        if preset == "Today":
            today_str = now.strftime("%Y-%m-%d")
            self.start_date_entry.insert(0, today_str)
            self.end_date_entry.insert(0, today_str)
        elif preset == "Yesterday":
            yest_str = (now - timedelta(days=1)).strftime("%Y-%m-%d")
            self.start_date_entry.insert(0, yest_str)
            self.end_date_entry.insert(0, yest_str)
        elif preset == "This Week":
            start_week = (now - timedelta(days=now.weekday())).strftime("%Y-%m-%d")
            self.start_date_entry.insert(0, start_week)
            self.end_date_entry.insert(0, now.strftime("%Y-%m-%d"))
        elif preset == "This Month":
            start_month = now.replace(day=1).strftime("%Y-%m-%d")
            self.start_date_entry.insert(0, start_month)
            self.end_date_entry.insert(0, now.strftime("%Y-%m-%d"))

    def on_department_changed(self, value: str) -> None:
        self.update_course_dropdown()

    def update_course_dropdown(self) -> None:
        dept_val = self.dept_menu.get()
        dept_id = self.dept_map.get(dept_val)
        
        courses = self.reports_controller.get_courses(dept_id)
        self.course_options = ["All Courses"] + [c.name for c in courses]
        self.course_map = {c.name: c.id for c in courses}
        self.course_menu.configure(values=self.course_options)
        self.course_menu.set("All Courses")

    def create_summary_card(self) -> None:
        """
        Renders the top summary card in the right container.
        """
        self.summary_card = Card(self.right_container)
        self.summary_card.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, ThemeManager.PAD_MD))
        self.summary_card.grid_columnconfigure((0, 1, 2, 3), weight=1)

        summary_lbl = ctk.CTkLabel(self.summary_card, text="Report Aggregations Summary", font=ThemeManager.get_font(size=12, weight="bold"), text_color=ThemeManager.get_color("text_muted"))
        summary_lbl.grid(row=0, column=0, columnspan=4, sticky="w", padx=ThemeManager.PAD_LG, pady=(ThemeManager.PAD_MD, 2))

        self.summary_labels = {}
        metrics = [
            ("Total Records", "0", 0),
            ("Present", "0", 1),
            ("Late", "0", 2),
            ("Attendance Rate", "0.0%", 3)
        ]

        for label_name, val, col in metrics:
            metric_frame = ctk.CTkFrame(self.summary_card, fg_color="transparent")
            metric_frame.grid(row=1, column=col, sticky="nsew", padx=ThemeManager.PAD_MD, pady=(2, ThemeManager.PAD_MD))
            
            lbl_key = ctk.CTkLabel(metric_frame, text=label_name, font=ThemeManager.get_font(size=10, weight="bold"), text_color=ThemeManager.get_color("text_muted"))
            lbl_key.pack(anchor="w")

            val_lbl = ctk.CTkLabel(
                metric_frame, 
                text=val, 
                font=ThemeManager.get_font(size=18, weight="bold"), 
                text_color=ThemeManager.get_color("text_primary")
            )
            val_lbl.pack(anchor="w", pady=2)
            self.summary_labels[label_name] = val_lbl

        self.summary_labels["Attendance Rate"].configure(text_color=ThemeManager.get_color("accent_success"))

    def create_preview_panel(self) -> None:
        """
        Initializes the preview table grid in the right panel.
        """
        self.preview_card = Card(self.right_container)
        self.preview_card.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.preview_card.grid_columnconfigure(0, weight=1)
        self.preview_card.grid_rowconfigure(1, weight=1)

        title = ctk.CTkLabel(
            self.preview_card,
            text="Report Preview Table",
            font=ThemeManager.get_font(size=12, weight="bold"),
            text_color=ThemeManager.get_color("text_muted")
        )
        title.grid(row=0, column=0, sticky="w", padx=ThemeManager.PAD_LG, pady=ThemeManager.PAD_MD)

        self.preview_table_frame = ctk.CTkFrame(self.preview_card, fg_color="transparent")
        self.preview_table_frame.grid(row=1, column=0, sticky="nsew", padx=ThemeManager.PAD_LG, pady=(0, ThemeManager.PAD_LG))
        self.preview_table_frame.grid_columnconfigure(0, weight=1)
        self.preview_table_frame.grid_rowconfigure(0, weight=1)

        self.render_empty_state()

    def render_empty_state(self) -> None:
        for w in self.preview_table_frame.winfo_children():
            w.destroy()

        panel = ctk.CTkFrame(self.preview_table_frame, fg_color="transparent")
        panel.grid(row=0, column=0)

        icon = ctk.CTkLabel(panel, text="📈", font=ThemeManager.get_font(size=40))
        icon.pack(pady=6)

        lbl = ctk.CTkLabel(
            panel,
            text="Report Preview Empty",
            font=ThemeManager.get_font(size=13, weight="bold"),
            text_color=ThemeManager.get_color("text_primary")
        )
        lbl.pack(pady=2)

        sub_lbl = ctk.CTkLabel(
            panel,
            text="Select filters and click 'Generate Report' above to preview check-in history.",
            font=ThemeManager.get_font(size=11),
            text_color=ThemeManager.get_color("text_muted")
        )
        sub_lbl.pack(pady=2)

    def trigger_generate_report(self) -> None:
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()

        # Validate
        valid, msg = self.reports_controller.validate_date_range(start_date, end_date)
        if not valid:
            MessageBox(self, title="Invalid Range", message=msg, icon_type="warning")
            return

        # Fetch optional filters
        status_val = self.status_menu.get()
        status = None if status_val == "All Statuses" else status_val

        source_val = self.source_menu.get()
        source = None if source_val == "All Sources" else source_val

        dept_val = self.dept_menu.get()
        dept_id = self.dept_map.get(dept_val)

        course_val = self.course_menu.get()
        course_id = self.course_map.get(course_val)

        stud_val = self.student_menu.get()
        student_id = self.student_map.get(stud_val)

        # Generate report
        report_data = self.reports_controller.generate_report(
            start_date=start_date,
            end_date=end_date,
            status=status,
            department_id=dept_id,
            course_id=course_id,
            source=source,
            student_id=student_id
        )

        records = report_data.get("records", [])
        if not records:
            MessageBox(self, title="No Records", message="No attendance records found for the selected filters.", icon_type="info")
            self.active_report_data = None
            self.export_csv_btn.configure(state="disabled")
            self.export_excel_btn.configure(state="disabled")
            self.render_empty_state()
            # Reset summary
            self.summary_labels["Total Records"].configure(text="0")
            self.summary_labels["Present"].configure(text="0")
            self.summary_labels["Late"].configure(text="0")
            self.summary_labels["Attendance Rate"].configure(text="0.0%")
            return

        self.active_report_data = report_data
        self.export_csv_btn.configure(state="normal")
        self.export_excel_btn.configure(state="normal")

        # Update Summary Labels
        summary = report_data["summary"]
        self.summary_labels["Total Records"].configure(text=str(summary["total_records"]))
        self.summary_labels["Present"].configure(text=str(summary["present"]))
        self.summary_labels["Late"].configure(text=str(summary["late"]))
        self.summary_labels["Attendance Rate"].configure(text=f"{summary['rate']}%")

        self.render_report_preview_table(records)

    def render_report_preview_table(self, records: list) -> None:
        for w in self.preview_table_frame.winfo_children():
            w.destroy()

        container = ctk.CTkFrame(self.preview_table_frame, fg_color="transparent")
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)

        # 1. Header Frame
        header = ctk.CTkFrame(container, fg_color=ThemeManager.get_color("bg_active"), height=30, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)

        cols = [
            ("Date", 0.15),
            ("Student ID", 0.20),
            ("Student Name", 0.30),
            ("Time", 0.15),
            ("Status", 0.10),
            ("Source", 0.10)
        ]

        curr_relx = 0.01
        for name, width in cols:
            lbl = ctk.CTkLabel(
                header,
                text=name,
                font=ThemeManager.get_font(size=10, weight="bold"),
                text_color=ThemeManager.get_color("text_primary")
            )
            lbl.place(relx=curr_relx, rely=0.5, relwidth=width-0.01, anchor="w")
            curr_relx += width

        # 2. Scroll Row frame
        scroll = ctk.CTkScrollableFrame(container, fg_color="transparent", corner_radius=0, height=260)
        scroll.grid(row=1, column=0, sticky="nsew", pady=(2, 0))
        scroll.grid_columnconfigure(0, weight=1)

        # Limit preview row loading to 100 for GUI performance
        preview_records = records[:100]

        for idx, r in enumerate(preview_records):
            row = ctk.CTkFrame(
                scroll,
                height=30,
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
            status_color = status_colors.get(r.status, ThemeManager.get_color("text_primary"))

            fields = [
                (r.date, 0.15, ThemeManager.get_color("text_light")),
                (r.student.student_code, 0.20, ThemeManager.get_color("text_primary")),
                (f"{r.student.first_name} {r.student.last_name}", 0.30, ThemeManager.get_color("text_primary")),
                (format_display_time(r.time_in), 0.15, ThemeManager.get_color("text_light")),
                (r.status, 0.10, status_color),
                (r.source, 0.10, ThemeManager.get_color("text_muted"))
            ]

            curr_relx = 0.01
            for text_val, width, color in fields:
                lbl = ctk.CTkLabel(
                    row,
                    text=text_val,
                    font=ThemeManager.get_font(size=10),
                    text_color=color,
                    anchor="w"
                )
                lbl.place(relx=curr_relx, rely=0.5, relwidth=width-0.01, anchor="w")
                curr_relx += width

        # Show notification if records are truncated in preview
        if len(records) > 100:
            info_lbl = ctk.CTkLabel(
                container,
                text=f"Showing first 100 rows out of {len(records)} matching records. Export full report to view all entries.",
                font=ThemeManager.get_font(size=10, slant="italic"),
                text_color=ThemeManager.get_color("text_muted")
            )
            info_lbl.grid(row=2, column=0, sticky="w", pady=4)

    def trigger_export_csv(self) -> None:
        if not self.active_report_data:
            return
        success, msg = self.reports_controller.export_csv(self.active_report_data)
        if success:
            MessageBox(self, title="Export Complete", message=msg, icon_type="success")
        else:
            MessageBox(self, title="Error", message=msg, icon_type="error")

    def trigger_export_excel(self) -> None:
        if not self.active_report_data:
            return
        success, msg = self.reports_controller.export_excel(self.active_report_data)
        if success:
            MessageBox(self, title="Export Complete", message=msg, icon_type="success")
        else:
            MessageBox(self, title="Error", message=msg, icon_type="error")
