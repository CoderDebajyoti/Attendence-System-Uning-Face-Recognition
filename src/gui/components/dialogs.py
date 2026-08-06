# ==============================================================================
# Face Recognition Attendance System - Reusable Dialog & Msg Box Widgets
# ==============================================================================

import customtkinter as ctk
from src.gui.themes import ThemeManager

class Dialog(ctk.CTkToplevel):
    """
    Base class for custom modal dialogs. Centered relative to parent 
    and traps input events via grab_set for a strict modal flow.
    """
    def __init__(self, parent, title: str = "Dialog", width: int = 400, height: int = 250):
        super().__init__(parent)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        
        # Configure modal hooks
        self.transient(parent)
        self.grab_set()
        
        # Center in parent coordinate frame
        self.center_window(parent, width, height)
        
        self.configure(fg_color=ThemeManager.get_color("bg_main"))
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=0, sticky="nsew", padx=ThemeManager.PAD_LG, pady=ThemeManager.PAD_LG)

    def center_window(self, parent, width: int, height: int) -> None:
        """
        Coordinates geometries to center this Toplevel relative to its parent window.
        """
        parent.update_idletasks()
        p_x = parent.winfo_x()
        p_y = parent.winfo_y()
        p_w = parent.winfo_width()
        p_h = parent.winfo_height()
        
        x = p_x + (p_w - width) // 2
        y = p_y + (p_h - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")


class MessageBox(Dialog):
    """
    A popup alert dialog with confirmation buttons, custom status icons, 
    and descriptive warning text blocks.
    """
    def __init__(self, parent, title: str, message: str, icon_type: str = "info", show_cancel: bool = False):
        super().__init__(parent, title, width=420, height=200)
        self.result = None
        
        # Visual theme mappings for icon status indicators
        icons = {
            "info": ("ℹ️", ThemeManager.get_color("accent_secondary")),
            "success": ("✅", ThemeManager.get_color("accent_success")),
            "warning": ("⚠️", ThemeManager.get_color("accent_warning")),
            "error": ("❌", ThemeManager.get_color("accent_danger"))
        }
        icon, color = icons.get(icon_type.lower(), ("ℹ️", ThemeManager.get_color("accent_secondary")))
        
        # Component layout inside dialog container
        self.container.grid_columnconfigure(1, weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        
        # Icon
        self.icon_label = ctk.CTkLabel(self.container, text=icon, font=ThemeManager.get_font(size=36), text_color=color)
        self.icon_label.grid(row=0, column=0, sticky="nw", padx=(0, ThemeManager.PAD_MD), pady=ThemeManager.PAD_MD)
        
        # Alert Message
        self.msg_label = ctk.CTkLabel(
            self.container, 
            text=message, 
            font=ThemeManager.get_font(size=13),
            text_color=ThemeManager.get_color("text_primary"),
            wraplength=300,
            justify="left"
        )
        self.msg_label.grid(row=0, column=1, sticky="nsew", pady=ThemeManager.PAD_MD)
        
        # Footer Action Area
        btn_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        btn_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(ThemeManager.PAD_MD, 0))
        
        # OK Button
        self.ok_btn = ctk.CTkButton(
            btn_frame,
            text="Confirm",
            font=ThemeManager.get_font(size=12, weight="bold"),
            fg_color=ThemeManager.get_color("accent_primary"),
            text_color=ThemeManager.get_color("text_dark"),
            hover_color=ThemeManager.get_color("bg_active"),
            width=90,
            command=self.on_confirm
        )
        self.ok_btn.pack(side="right", padx=ThemeManager.PAD_XS)
        
        if show_cancel:
            self.cancel_btn = ctk.CTkButton(
                btn_frame,
                text="Cancel",
                font=ThemeManager.get_font(size=12),
                fg_color="transparent",
                border_color=ThemeManager.get_color("border"),
                border_width=1,
                text_color=ThemeManager.get_color("text_light"),
                hover_color=ThemeManager.get_color("bg_active"),
                width=90,
                command=self.on_cancel
            )
            self.cancel_btn.pack(side="right", padx=ThemeManager.PAD_XS)

    def on_confirm(self) -> None:
        self.result = True
        self.destroy()
        
    def on_cancel(self) -> None:
        self.result = False
        self.destroy()
