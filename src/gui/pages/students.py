# ==============================================================================
# Face Recognition Attendance System - Students Registry Page View
# ==============================================================================

import customtkinter as ctk
from datetime import datetime
from src.gui.themes import ThemeManager
from src.gui.pages.base import BasePage
from src.gui.components import Card, Dialog, MessageBox
from src.controllers import StudentController

class StudentsPage(BasePage):
    """
    Students Management Page View. Implements the list, filter, search,
    and coordinates modal dialogs for CRUD transactions.
    """
    def __init__(self, parent, controller) -> None:
        self.student_controller = StudentController()
        
        # Keep track of active filters
        self.search_val = ""
        self.selected_dept_id = None
        self.selected_course_id = None
        self.selected_year = None
        self.selected_status = None
        self.selected_face_status = None
        
        super().__init__(
            parent=parent,
            controller=controller,
            title="Student Management",
            description="Register student profiles, maintain enrolment statuses, and link biometric datasets.",
            phase=7
        )

    def show_default_placeholder(self) -> None:
        """
        Overrides the base method to render the actual Student Management UI.
        """
        # Configure layout grids inside content area
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=1)  # Table expands vertically
        
        # 1. Search and Filter Panel (Top)
        self.create_filter_panel()
        
        # 2. Main Data Canvas (Table View or Empty State)
        self.data_canvas = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.data_canvas.grid(row=1, column=0, sticky="nsew", pady=(ThemeManager.PAD_MD, 0))
        self.data_canvas.grid_columnconfigure(0, weight=1)
        self.data_canvas.grid_rowconfigure(0, weight=1)
        
        # Load and render table list
        self.refresh_student_list()

    def create_filter_panel(self) -> None:
        """
        Renders the search and filter option widgets at the top.
        """
        panel = Card(self.content_frame)
        panel.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        
        # Configure filter panel internal grid
        panel.grid_columnconfigure((0, 1, 2, 3), weight=1)
        panel.grid_columnconfigure(4, weight=0) # Action buttons fixed width
        
        # Row 0: Search and Add Button
        search_frame = ctk.CTkFrame(panel, fg_color="transparent")
        search_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=ThemeManager.PAD_MD, pady=ThemeManager.PAD_SM)
        
        self.search_entry = ctk.CTkEntry(
            search_frame, 
            placeholder_text="Search by ID, Name, Roll No, Email...",
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

        # Action: Add Student Button
        add_btn = ctk.CTkButton(
            panel,
            text="  +  Add Student",
            font=ThemeManager.get_font(size=12, weight="bold"),
            fg_color=ThemeManager.get_color("accent_primary"),
            text_color=ThemeManager.get_color("text_dark"),
            hover_color=ThemeManager.get_color("bg_active"),
            height=32,
            command=self.open_add_dialog
        )
        add_btn.grid(row=0, column=3, columnspan=2, sticky="e", padx=ThemeManager.PAD_MD, pady=ThemeManager.PAD_SM)

        # Row 1: Dropdown filters
        # Departments list dropdown
        depts = self.student_controller.get_departments()
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

        # Courses list dropdown
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

        # Status dropdown
        self.status_menu = ctk.CTkOptionMenu(
            panel,
            values=["All Statuses", "Active", "Inactive", "Graduated", "Suspended"],
            font=ThemeManager.get_font(size=11),
            dropdown_font=ThemeManager.get_font(size=11),
            height=28,
            fg_color=ThemeManager.get_color("bg_active"),
            button_color=ThemeManager.get_color("bg_active"),
            text_color=ThemeManager.get_color("text_primary"),
            command=self.on_status_filter_changed
        )
        self.status_menu.grid(row=1, column=2, sticky="ew", padx=ThemeManager.PAD_MD, pady=ThemeManager.PAD_SM)

        # Face Status dropdown
        self.face_menu = ctk.CTkOptionMenu(
            panel,
            values=["All Face Statuses", "Not Registered", "Collecting", "Ready", "Needs Update"],
            font=ThemeManager.get_font(size=11),
            dropdown_font=ThemeManager.get_font(size=11),
            height=28,
            fg_color=ThemeManager.get_color("bg_active"),
            button_color=ThemeManager.get_color("bg_active"),
            text_color=ThemeManager.get_color("text_primary"),
            command=self.on_face_filter_changed
        )
        self.face_menu.grid(row=1, column=3, sticky="ew", padx=ThemeManager.PAD_MD, pady=ThemeManager.PAD_SM)

        # Reset button
        reset_btn = ctk.CTkButton(
            panel,
            text="Reset Filters",
            font=ThemeManager.get_font(size=11),
            fg_color="transparent",
            border_color=ThemeManager.get_color("border"),
            border_width=1,
            text_color=ThemeManager.get_color("text_light"),
            hover_color=ThemeManager.get_color("bg_active"),
            width=100,
            height=28,
            command=self.reset_filters
        )
        reset_btn.grid(row=1, column=4, sticky="e", padx=ThemeManager.PAD_MD, pady=ThemeManager.PAD_SM)

    def update_course_dropdown(self) -> None:
        """
        Reloads course catalog options depending on the chosen department.
        """
        courses = self.student_controller.get_courses(self.selected_dept_id)
        self.course_options = ["All Courses"] + [c.name for c in courses]
        self.course_map = {c.name: c.id for c in courses}
        self.course_menu.configure(values=self.course_options)
        self.course_menu.set("All Courses")
        self.selected_course_id = None

    def trigger_search(self) -> None:
        self.search_val = self.search_entry.get().strip()
        self.refresh_student_list()

    def on_department_filter_changed(self, value: str) -> None:
        self.selected_dept_id = self.dept_map.get(value)
        self.update_course_dropdown()
        self.refresh_student_list()

    def on_course_filter_changed(self, value: str) -> None:
        self.selected_course_id = self.course_map.get(value)
        self.refresh_student_list()

    def on_status_filter_changed(self, value: str) -> None:
        self.selected_status = None if value == "All Statuses" else value
        self.refresh_student_list()

    def on_face_filter_changed(self, value: str) -> None:
        self.selected_face_status = None if value == "All Face Statuses" else value
        self.refresh_student_list()

    def reset_filters(self) -> None:
        self.search_entry.delete(0, "end")
        self.search_val = ""
        self.selected_dept_id = None
        self.selected_course_id = None
        self.selected_year = None
        self.selected_status = None
        self.selected_face_status = None
        
        self.dept_menu.set("All Departments")
        self.update_course_dropdown()
        self.status_menu.set("All Statuses")
        self.face_menu.set("All Face Statuses")
        
        self.refresh_student_list()

    def refresh_student_list(self) -> None:
        """
        Clears the data canvas and rebuilds the student table grid or empty state card.
        """
        # Clear data canvas child panels
        for widget in self.data_canvas.winfo_children():
            widget.destroy()
            
        students = self.student_controller.get_filtered_students(
            search_query=self.search_val,
            department_id=self.selected_dept_id,
            course_id=self.selected_course_id,
            year=self.selected_year,
            status=self.selected_status,
            face_status=self.selected_face_status
        )

        if not students:
            self.render_empty_state()
        else:
            self.render_students_table(students)

    def render_empty_state(self) -> None:
        """
        Displays a styled card layout when no student records match the filters.
        """
        card = Card(self.data_canvas)
        card.grid(row=0, column=0, sticky="nsew", padx=ThemeManager.PAD_MD, pady=ThemeManager.PAD_MD)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)
        
        panel = ctk.CTkFrame(card, fg_color="transparent")
        panel.grid(row=0, column=0)
        
        icon = ctk.CTkLabel(panel, text="👥", font=ThemeManager.get_font(size=48))
        icon.pack(pady=10)
        
        lbl1 = ctk.CTkLabel(
            panel, 
            text="No Students Registered Yet", 
            font=ThemeManager.get_font(size=16, weight="bold"),
            text_color=ThemeManager.get_color("text_primary")
        )
        lbl1.pack(pady=5)
        
        lbl2 = ctk.CTkLabel(
            panel, 
            text="Use the filters above or click the button below to onboard a new student profile.", 
            font=ThemeManager.get_font(size=12),
            text_color=ThemeManager.get_color("text_muted")
        )
        lbl2.pack(pady=(0, 20))
        
        btn = ctk.CTkButton(
            panel,
            text="Add Student",
            font=ThemeManager.get_font(size=12, weight="bold"),
            fg_color=ThemeManager.get_color("accent_primary"),
            text_color=ThemeManager.get_color("text_dark"),
            hover_color=ThemeManager.get_color("bg_active"),
            width=130,
            command=self.open_add_dialog
        )
        btn.pack()

    def render_students_table(self, students: list) -> None:
        """
        Renders a scrollable grid list containing student items.
        """
        container = Card(self.data_canvas)
        container.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)
        
        # 1. Table Header
        header = ctk.CTkFrame(container, fg_color=ThemeManager.get_color("bg_active"), height=36, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        
        # Define table grid columns
        columns = [
            ("Student ID", 0.15),
            ("Name", 0.20),
            ("Roll No", 0.12),
            ("Department", 0.12),
            ("Course", 0.15),
            ("Status", 0.10),
            ("Face ID", 0.10),
            ("Actions", 0.16)  # View / Edit / Delete buttons
        ]
        
        # Render header labels
        curr_relx = 0.01
        for col_name, col_width in columns:
            lbl = ctk.CTkLabel(
                header,
                text=col_name,
                font=ThemeManager.get_font(size=11, weight="bold"),
                text_color=ThemeManager.get_color("text_primary")
            )
            lbl.place(relx=curr_relx, rely=0.2, relwidth=col_width-0.01, anchor="w")
            curr_relx += col_width

        # 2. Table Rows Scroll Area
        scroll_area = ctk.CTkScrollableFrame(container, fg_color="transparent", corner_radius=0)
        scroll_area.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
        scroll_area.grid_columnconfigure(0, weight=1)
        
        # Render each row
        for idx, student in enumerate(students):
            row = ctk.CTkFrame(
                scroll_area, 
                height=42, 
                fg_color="transparent" if idx % 2 == 0 else ThemeManager.get_color("bg_main"),
                corner_radius=4
            )
            row.grid(row=idx, column=0, sticky="ew", pady=1)
            row.grid_propagate(False)
            
            # Map status visual colors
            status_colors = {
                "Active": ThemeManager.get_color("accent_success"),
                "Inactive": ThemeManager.get_color("text_muted"),
                "Graduated": ThemeManager.get_color("accent_secondary"),
                "Suspended": ThemeManager.get_color("accent_danger")
            }
            status_color = status_colors.get(student.status, ThemeManager.get_color("text_primary"))
            
            face_colors = {
                "Ready": ThemeManager.get_color("accent_success"),
                "Not Registered": ThemeManager.get_color("accent_danger"),
                "Collecting": ThemeManager.get_color("accent_warning"),
                "Needs Update": ThemeManager.get_color("accent_warning")
            }
            face_color = face_colors.get(student.face_dataset_status, ThemeManager.get_color("text_primary"))
            
            # Values registry
            values = [
                (student.student_code, 0.15, ThemeManager.get_color("text_primary"), "w"),
                (f"{student.first_name} {student.last_name}", 0.20, ThemeManager.get_color("text_primary"), "w"),
                (student.roll_number or "-", 0.12, ThemeManager.get_color("text_light"), "w"),
                (student.department.code, 0.12, ThemeManager.get_color("text_muted"), "w"),
                (student.course.code, 0.15, ThemeManager.get_color("text_muted"), "w"),
                (student.status, 0.10, status_color, "w"),
                (student.face_dataset_status, 0.10, face_color, "w")
            ]
            
            # Draw row value labels
            curr_relx = 0.01
            for val_text, col_width, text_color, anchor in values:
                lbl = ctk.CTkLabel(
                    row,
                    text=val_text,
                    font=ThemeManager.get_font(size=11),
                    text_color=text_color,
                    anchor=anchor
                )
                lbl.place(relx=curr_relx, rely=0.5, relwidth=col_width-0.01, anchor="w")
                curr_relx += col_width
                
            # Draw Row Action Buttons
            btn_frame = ctk.CTkFrame(row, fg_color="transparent")
            btn_frame.place(relx=curr_relx, rely=0.5, relwidth=0.16, relheight=0.8, anchor="w")
            
            # View Button
            v_btn = ctk.CTkButton(
                btn_frame, text="👁️", font=ThemeManager.get_font(size=10),
                fg_color="transparent", width=22, hover_color=ThemeManager.get_color("bg_active"),
                text_color=ThemeManager.get_color("accent_secondary"),
                command=lambda s_id=student.id: self.open_view_dialog(s_id)
            )
            v_btn.pack(side="left", padx=2)
            
            # Edit Button
            e_btn = ctk.CTkButton(
                btn_frame, text="⚙️", font=ThemeManager.get_font(size=10),
                fg_color="transparent", width=22, hover_color=ThemeManager.get_color("bg_active"),
                text_color=ThemeManager.get_color("accent_primary"),
                command=lambda s_id=student.id: self.open_edit_dialog(s_id)
            )
            e_btn.pack(side="left", padx=2)
            
            # Delete Button
            d_btn = ctk.CTkButton(
                btn_frame, text="🗑️", font=ThemeManager.get_font(size=10),
                fg_color="transparent", width=22, hover_color=ThemeManager.get_color("bg_active"),
                text_color=ThemeManager.get_color("accent_danger"),
                command=lambda s_id=student.id: self.confirm_delete_student(s_id)
            )
            d_btn.pack(side="left", padx=2)

    def open_add_dialog(self) -> None:
        """
        Spawns the StudentFormDialog configured in Add Mode.
        """
        dialog = StudentFormDialog(self, title="Register Student Profile", controller=self.student_controller)
        self.wait_window(dialog)
        self.refresh_student_list()

    def open_edit_dialog(self, student_id: int) -> None:
        """
        Spawns the StudentFormDialog configured in Edit Mode.
        """
        dialog = StudentFormDialog(self, title="Modify Student Profile", controller=self.student_controller, student_id=student_id)
        self.wait_window(dialog)
        self.refresh_student_list()

    def open_view_dialog(self, student_id: int) -> None:
        """
        Spawns the StudentDetailDialog modal overlay.
        """
        dialog = StudentDetailDialog(self, student_id=student_id, controller=self.student_controller)
        self.wait_window(dialog)

    def confirm_delete_student(self, student_id: int) -> None:
        """
        Prompts warning confirm box before deletion.
        """
        student = self.student_controller.get_student_details(student_id)
        if not student:
            return
            
        msg = (
            f"Are you sure you want to delete student: {student.first_name} {student.last_name} ({student.student_code})?\n\n"
            "Warning: Deleting this student record will permanently remove all associated biometric "
            "face embedding templates and attendance check-in history records."
        )
        
        confirm = MessageBox(self, title="Delete Student", message=msg, icon_type="warning", show_cancel=True)
        self.wait_window(confirm)
        
        if confirm.result:
            success = self.student_controller.delete_student(student_id)
            if success:
                alert = MessageBox(self, title="Success", message="Student deleted successfully.", icon_type="success")
                self.wait_window(alert)
                self.refresh_student_list()
            else:
                alert = MessageBox(self, title="Error", message="Could not complete deletion.", icon_type="error")
                self.wait_window(alert)


class StudentFormDialog(Dialog):
    """
    Form dialog supporting profile additions and modifications.
    """
    def __init__(self, parent, title: str, controller: StudentController, student_id: int = None) -> None:
        self.controller = controller
        self.student_id = student_id
        self.is_edit = student_id is not None
        
        # Dimensions setup
        super().__init__(parent, title, width=720, height=580)
        
        # Generate Form Fields
        self.build_form_layout()
        
        # Populate values if Edit mode
        if self.is_edit:
            self.load_student_data()

    def build_form_layout(self) -> None:
        # Partition form container in 2 columns
        self.container.grid_columnconfigure((0, 1), weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        
        # Left Side Column Frame
        left_col = ctk.CTkFrame(self.container, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, ThemeManager.PAD_MD))
        
        # Right Side Column Frame
        right_col = ctk.CTkFrame(self.container, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew", padx=(ThemeManager.PAD_MD, 0))
        
        # Setup Left Column Inputs
        self.code_input = self.add_input_row(left_col, "Student ID (Code)*", "e.g. STD2026001")
        self.roll_input = self.add_input_row(left_col, "Roll Number", "e.g. CSE-26-042")
        self.first_input = self.add_input_row(left_col, "First Name*", "")
        self.last_input = self.add_input_row(left_col, "Last Name*", "")
        self.dob_input = self.add_input_row(left_col, "Date of Birth (YYYY-MM-DD)*", "YYYY-MM-DD")
        
        self.gender_menu = self.add_dropdown_row(left_col, "Gender*", ["Male", "Female", "Other"])
        
        # Setup Right Column Inputs
        self.email_input = self.add_input_row(right_col, "Institutional Email*", "e.g. name@univ.edu")
        self.phone_input = self.add_input_row(right_col, "Phone Number*", "e.g. +91 9999999999")
        self.address_input = self.add_input_row(right_col, "Residential Address", "")
        
        # Dynamic Dept and Course dropdowns
        self.depts = self.controller.get_departments()
        dept_names = [d.name for d in self.depts]
        self.dept_map = {d.name: d.id for d in self.depts}
        self.dept_reverse_map = {d.id: d.name for d in self.depts}
        
        self.dept_menu = self.add_dropdown_row(
            right_col, 
            "Department*", 
            dept_names, 
            callback=self.on_form_department_changed
        )
        
        self.course_menu_var = ctk.StringVar(value="")
        self.course_menu = self.add_dropdown_row_var(
            right_col,
            "Course*",
            [],
            self.course_menu_var
        )
        self.update_form_courses()

        self.year_menu = self.add_dropdown_row(right_col, "Academic Year*", ["1", "2", "3", "4"])
        self.semester_menu = self.add_dropdown_row(right_col, "Semester*", ["1", "2", "3", "4", "5", "6", "7", "8"])
        
        # Date default configuration
        today_date = datetime.now().strftime("%Y-%m-%d")
        self.enroll_input = self.add_input_row(right_col, "Enrollment Date (YYYY-MM-DD)*", today_date)
        self.enroll_input.insert(0, today_date)
        
        self.status_menu = self.add_dropdown_row(right_col, "Status*", ["Active", "Inactive", "Graduated", "Suspended"])
        
        # Bottom Actions Bar
        actions_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        actions_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(ThemeManager.PAD_MD, 0))
        
        save_btn = ctk.CTkButton(
            actions_frame,
            text="Save Profile",
            font=ThemeManager.get_font(size=12, weight="bold"),
            fg_color=ThemeManager.get_color("accent_primary"),
            text_color=ThemeManager.get_color("text_dark"),
            hover_color=ThemeManager.get_color("bg_active"),
            width=110,
            command=self.submit_form
        )
        save_btn.pack(side="right", padx=ThemeManager.PAD_XS)

        cancel_btn = ctk.CTkButton(
            actions_frame,
            text="Cancel",
            font=ThemeManager.get_font(size=12),
            fg_color="transparent",
            border_color=ThemeManager.get_color("border"),
            border_width=1,
            text_color=ThemeManager.get_color("text_light"),
            hover_color=ThemeManager.get_color("bg_active"),
            width=90,
            command=self.destroy
        )
        cancel_btn.pack(side="right", padx=ThemeManager.PAD_XS)

    def add_input_row(self, parent, label_text: str, placeholder: str) -> ctk.CTkEntry:
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=4)
        
        lbl = ctk.CTkLabel(row, text=label_text, font=ThemeManager.get_font(size=11, weight="bold"), text_color=ThemeManager.get_color("text_light"))
        lbl.pack(anchor="w")
        
        entry = ctk.CTkEntry(row, placeholder_text=placeholder, font=ThemeManager.get_font(size=11), height=28)
        entry.pack(fill="x", pady=2)
        return entry

    def add_dropdown_row(self, parent, label_text: str, values: list, callback=None) -> ctk.CTkOptionMenu:
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=4)
        
        lbl = ctk.CTkLabel(row, text=label_text, font=ThemeManager.get_font(size=11, weight="bold"), text_color=ThemeManager.get_color("text_light"))
        lbl.pack(anchor="w")
        
        menu = ctk.CTkOptionMenu(
            row,
            values=values,
            font=ThemeManager.get_font(size=11),
            dropdown_font=ThemeManager.get_font(size=11),
            height=28,
            fg_color=ThemeManager.get_color("bg_active"),
            button_color=ThemeManager.get_color("bg_active"),
            text_color=ThemeManager.get_color("text_primary"),
            command=callback
        )
        menu.pack(fill="x", pady=2)
        return menu

    def add_dropdown_row_var(self, parent, label_text: str, values: list, variable: ctk.StringVar) -> ctk.CTkOptionMenu:
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=4)
        
        lbl = ctk.CTkLabel(row, text=label_text, font=ThemeManager.get_font(size=11, weight="bold"), text_color=ThemeManager.get_color("text_light"))
        lbl.pack(anchor="w")
        
        menu = ctk.CTkOptionMenu(
            row,
            values=values,
            variable=variable,
            font=ThemeManager.get_font(size=11),
            dropdown_font=ThemeManager.get_font(size=11),
            height=28,
            fg_color=ThemeManager.get_color("bg_active"),
            button_color=ThemeManager.get_color("bg_active"),
            text_color=ThemeManager.get_color("text_primary")
        )
        menu.pack(fill="x", pady=2)
        return menu

    def on_form_department_changed(self, value: str) -> None:
        self.update_form_courses()

    def update_form_courses(self) -> None:
        """
        Dynamically modifies available course selection values inside dropdown.
        """
        dept_name = self.dept_menu.get()
        dept_id = self.dept_map.get(dept_name)
        
        courses = self.controller.get_courses(dept_id)
        course_names = [c.name for c in courses]
        self.form_course_map = {c.name: c.id for c in courses}
        self.form_course_reverse_map = {c.id: c.name for c in courses}
        
        self.course_menu.configure(values=course_names)
        if course_names:
            self.course_menu_var.set(course_names[0])
        else:
            self.course_menu_var.set("")

    def load_student_data(self) -> None:
        """
        Pre-populates fields with existing data during Edit mode.
        """
        student = self.controller.get_student_details(self.student_id)
        if not student:
            return
            
        # Code field locked during edits
        self.code_input.insert(0, student.student_code)
        self.code_input.configure(state="disabled")
        
        if student.roll_number:
            self.roll_input.insert(0, student.roll_number)
        self.first_input.insert(0, student.first_name)
        self.last_input.insert(0, student.last_name)
        self.dob_input.insert(0, student.date_of_birth)
        self.gender_menu.set(student.gender)
        
        self.email_input.insert(0, student.email)
        self.phone_input.insert(0, student.phone)
        if student.address:
            self.address_input.insert(0, student.address)
            
        # Set department dropdown
        dept_name = self.dept_reverse_map.get(student.department_id)
        if dept_name:
            self.dept_menu.set(dept_name)
            
        # Update course lists
        self.update_form_courses()
        course_name = self.form_course_reverse_map.get(student.course_id)
        if course_name:
            self.course_menu_var.set(course_name)
            
        self.year_menu.set(str(student.year))
        self.semester_menu.set(str(student.semester))
        
        self.enroll_input.delete(0, "end")
        self.enroll_input.insert(0, student.enrollment_date)
        self.status_menu.set(student.status)

    def submit_form(self) -> None:
        """
        Assembles field inputs and calls controller.
        """
        dept_name = self.dept_menu.get()
        course_name = self.course_menu_var.get()
        
        dept_id = self.dept_map.get(dept_name)
        course_id = self.form_course_map.get(course_name)

        student_data = {
            "student_code": self.code_input.get(),
            "roll_number": self.roll_input.get(),
            "first_name": self.first_input.get(),
            "last_name": self.last_input.get(),
            "date_of_birth": self.dob_input.get(),
            "gender": self.gender_menu.get(),
            "email": self.email_input.get(),
            "phone": self.phone_input.get(),
            "address": self.address_input.get(),
            "department_id": dept_id,
            "course_id": course_id,
            "year": self.year_menu.get(),
            "semester": self.semester_menu.get(),
            "enrollment_date": self.enroll_input.get(),
            "status": self.status_menu.get()
        }

        # Submit transaction
        success, message = self.controller.save_student(
            student_data=student_data, 
            is_edit=self.is_edit, 
            student_id=self.student_id
        )

        if success:
            alert = MessageBox(self, title="Success", message=message, icon_type="success")
            self.wait_window(alert)
            self.destroy()
        else:
            alert = MessageBox(self, title="Validation Error", message=message, icon_type="error")
            self.wait_window(alert)


class StudentDetailDialog(Dialog):
    """
    Renders detailed profile cards of a student record.
    """
    def __init__(self, parent, student_id: int, controller: StudentController) -> None:
        self.controller = controller
        self.student_id = student_id
        
        super().__init__(parent, "Student Profile Details", width=640, height=580)
        self.build_details_layout()

    def build_details_layout(self) -> None:
        student = self.controller.get_student_details(self.student_id)
        if not student:
            self.destroy()
            return
            
        self.container.grid_columnconfigure((0, 1), weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        
        # Scrollable panel to allow details viewing
        scroll = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        scroll.grid(row=0, column=0, columnspan=2, sticky="nsew")
        scroll.grid_columnconfigure((0, 1), weight=1)

        # Helper to render visual key-value items
        def add_info_row(panel, key: str, value: str):
            row = ctk.CTkFrame(panel, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            lbl_key = ctk.CTkLabel(row, text=f"{key}:", font=ThemeManager.get_font(size=11, weight="bold"), text_color=ThemeManager.get_color("text_muted"), width=120, anchor="w")
            lbl_key.pack(side="left")
            
            lbl_val = ctk.CTkLabel(row, text=str(value), font=ThemeManager.get_font(size=11), text_color=ThemeManager.get_color("text_primary"), anchor="w")
            lbl_val.pack(side="left", fill="x", expand=True)

        # 1. Personal Details Card
        c1 = Card(scroll)
        c1.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        lbl1 = ctk.CTkLabel(c1, text="Personal Details", font=ThemeManager.get_font(size=12, weight="bold"), text_color=ThemeManager.get_color("accent_primary"))
        lbl1.pack(anchor="w", padx=ThemeManager.PAD_MD, pady=(ThemeManager.PAD_SM, ThemeManager.PAD_XS))
        
        add_info_row(c1, "First Name", student.first_name)
        add_info_row(c1, "Last Name", student.last_name)
        add_info_row(c1, "Date of Birth", student.date_of_birth)
        add_info_row(c1, "Gender", student.gender)

        # 2. Contact Details Card
        c2 = Card(scroll)
        c2.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)
        lbl2 = ctk.CTkLabel(c2, text="Contact Information", font=ThemeManager.get_font(size=12, weight="bold"), text_color=ThemeManager.get_color("accent_primary"))
        lbl2.pack(anchor="w", padx=ThemeManager.PAD_MD, pady=(ThemeManager.PAD_SM, ThemeManager.PAD_XS))
        
        add_info_row(c2, "Email", student.email)
        add_info_row(c2, "Phone", student.phone)
        add_info_row(c2, "Address", student.address or "-")

        # 3. Academic Details Card
        c3 = Card(scroll)
        c3.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)
        lbl3 = ctk.CTkLabel(c3, text="Academic Allocation", font=ThemeManager.get_font(size=12, weight="bold"), text_color=ThemeManager.get_color("accent_primary"))
        lbl3.pack(anchor="w", padx=ThemeManager.PAD_MD, pady=(ThemeManager.PAD_SM, ThemeManager.PAD_XS))
        
        add_info_row(c3, "Department", student.department.name)
        add_info_row(c3, "Course", student.course.name)
        add_info_row(c3, "Year", f"Year {student.year}")
        add_info_row(c3, "Semester", f"Semester {student.semester}")

        # 4. Enrollment Details Card
        c4 = Card(scroll)
        c4.grid(row=1, column=1, sticky="nsew", padx=4, pady=4)
        lbl4 = ctk.CTkLabel(c4, text="Enrollment Profile", font=ThemeManager.get_font(size=12, weight="bold"), text_color=ThemeManager.get_color("accent_primary"))
        lbl4.pack(anchor="w", padx=ThemeManager.PAD_MD, pady=(ThemeManager.PAD_SM, ThemeManager.PAD_XS))
        
        add_info_row(c4, "Student ID", student.student_code)
        add_info_row(c4, "Roll Number", student.roll_number or "-")
        add_info_row(c4, "Enrollment Date", student.enrollment_date)
        add_info_row(c4, "Status", student.status)

        # 5. Biometric dataset Panel
        c5 = Card(scroll)
        c5.grid(row=2, column=0, columnspan=2, sticky="ew", padx=4, pady=8)
        lbl5 = ctk.CTkLabel(c5, text="Biometric Face Dataset", font=ThemeManager.get_font(size=12, weight="bold"), text_color=ThemeManager.get_color("accent_primary"))
        lbl5.pack(anchor="w", padx=ThemeManager.PAD_MD, pady=(ThemeManager.PAD_SM, ThemeManager.PAD_XS))
        
        # Display dataset indicators
        status_panel = ctk.CTkFrame(c5, fg_color="transparent")
        status_panel.pack(fill="x", padx=ThemeManager.PAD_LG, pady=2)
        
        from src.controllers import DatasetController
        dataset_ctrl = DatasetController()
        dataset = dataset_ctrl.get_dataset_details(student.id)
        img_count = dataset.image_count if dataset else 0
        target_count = dataset_ctrl.get_target_image_count()
        
        # Fetch recognition service details
        from src.services.face_recognition_service import FaceRecognitionService
        rec_service = FaceRecognitionService.get_instance()
        is_registered = rec_service.is_student_in_model(student.id)
        rec_profile = "REGISTERED" if is_registered else "NOT REGISTERED"
        
        metadata = rec_service.metadata
        last_update = "-"
        if metadata and "updated_at" in metadata:
            try:
                dt = datetime.fromisoformat(metadata["updated_at"])
                last_update = dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                last_update = metadata["updated_at"]

        add_info_row(status_panel, "Face Dataset", student.face_dataset_status)
        add_info_row(status_panel, "Captured Frames", f"{img_count} / {target_count} Images")
        add_info_row(status_panel, "Recognition Profile", rec_profile)
        add_info_row(status_panel, "Last Model Update", last_update)
        
        def manage_dataset_click():
            self.destroy()
            app = self.master.controller
            app.navigation_manager.show_page("Dataset")
            dataset_page = app.page_manager.pages.get("Dataset")
            if dataset_page:
                dataset_page.select_student_by_id(student.id)

        btn = ctk.CTkButton(
            c5,
            text="Manage Biometric Dataset",
            font=ThemeManager.get_font(size=11, weight="bold"),
            fg_color=ThemeManager.get_color("accent_primary"),
            text_color=ThemeManager.get_color("text_dark"),
            hover_color=ThemeManager.get_color("bg_active"),
            command=manage_dataset_click
        )
        btn.pack(pady=ThemeManager.PAD_MD)

        # 6. Attendance Summary & History Panel
        c6 = Card(scroll)
        c6.grid(row=3, column=0, columnspan=2, sticky="ew", padx=4, pady=8)
        lbl6 = ctk.CTkLabel(c6, text="Attendance Summary & History", font=ThemeManager.get_font(size=12, weight="bold"), text_color=ThemeManager.get_color("accent_primary"))
        lbl6.pack(anchor="w", padx=ThemeManager.PAD_MD, pady=(ThemeManager.PAD_SM, ThemeManager.PAD_XS))

        from src.controllers.attendance_controller import AttendanceController
        att_ctrl = AttendanceController()
        att_summary = att_ctrl.get_student_attendance_summary(student.id)
        
        summary_panel = ctk.CTkFrame(c6, fg_color="transparent")
        summary_panel.pack(fill="x", padx=ThemeManager.PAD_LG, pady=2)
        
        add_info_row(summary_panel, "Total Sessions", str(att_summary["total"]))
        add_info_row(summary_panel, "Present Sessions", str(att_summary["present"]))
        add_info_row(summary_panel, "Late Sessions", str(att_summary["late"]))
        add_info_row(summary_panel, "Attendance Rate", f"{att_summary['rate']}%")

        # Recent Attendance History logs
        recent_lbl = ctk.CTkLabel(c6, text="Recent Attendance Logs", font=ThemeManager.get_font(size=11, weight="bold"), text_color=ThemeManager.get_color("text_light"))
        recent_lbl.pack(anchor="w", padx=ThemeManager.PAD_LG, pady=(ThemeManager.PAD_SM, ThemeManager.PAD_XS))

        recent_logs = att_ctrl.get_student_attendance_history(student.id, limit=5)
        if not recent_logs:
            no_logs_lbl = ctk.CTkLabel(c6, text="No attendance recorded yet.", font=ThemeManager.get_font(size=11), text_color=ThemeManager.get_color("text_muted"))
            no_logs_lbl.pack(anchor="w", padx=ThemeManager.PAD_LG, pady=2)
        else:
            log_table_frame = ctk.CTkFrame(c6, fg_color=ThemeManager.get_color("bg_active"), corner_radius=ThemeManager.CORNER_RADIUS_SM)
            log_table_frame.pack(fill="x", padx=ThemeManager.PAD_LG, pady=4)
            
            for idx, log in enumerate(recent_logs):
                log_row = ctk.CTkFrame(log_table_frame, height=26, fg_color="transparent" if idx % 2 == 0 else ThemeManager.get_color("bg_main"))
                log_row.pack(fill="x", pady=1)
                
                date_txt = log.date
                time_txt = format_display_time(log.time_in)
                status_txt = log.status
                source_txt = log.source
                
                status_colors = {
                    "PRESENT": ThemeManager.get_color("accent_success"),
                    "LATE": ThemeManager.get_color("accent_warning"),
                    "ABSENT": ThemeManager.get_color("accent_danger"),
                    "EXCUSED": ThemeManager.get_color("accent_secondary")
                }
                status_color = status_colors.get(status_txt, ThemeManager.get_color("text_primary"))

                lbl_date = ctk.CTkLabel(log_row, text=date_txt, font=ThemeManager.get_font(size=10), width=90, anchor="w")
                lbl_date.pack(side="left", padx=4)
                
                lbl_time = ctk.CTkLabel(log_row, text=time_txt, font=ThemeManager.get_font(size=10), width=80, anchor="w")
                lbl_time.pack(side="left", padx=4)
                
                lbl_status = ctk.CTkLabel(log_row, text=status_txt, font=ThemeManager.get_font(size=10, weight="bold"), text_color=status_color, width=90, anchor="w")
                lbl_status.pack(side="left", padx=4)
                
                lbl_src = ctk.CTkLabel(log_row, text=f"Source: {source_txt}", font=ThemeManager.get_font(size=10), text_color=ThemeManager.get_color("text_muted"), anchor="w")
                lbl_src.pack(side="left", fill="x", expand=True, padx=4)

        # Bottom Close Button
        close_btn = ctk.CTkButton(
            self.container,
            text="Close",
            font=ThemeManager.get_font(size=12),
            fg_color=ThemeManager.get_color("bg_active"),
            text_color=ThemeManager.get_color("text_primary"),
            hover_color=ThemeManager.get_color("bg_card"),
            width=100,
            command=self.destroy
        )
        close_btn.grid(row=1, column=0, columnspan=2, pady=(ThemeManager.PAD_MD, 0))
