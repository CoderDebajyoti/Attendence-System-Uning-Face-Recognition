# ==============================================================================
# Face Recognition Attendance System - Navigation Manager
# ==============================================================================

class NavigationManager:
    """
    Coordinates page transitions, sidebar item selection states, breadcrumb 
    updates, and registers routing mappings between buttons and page containers.
    """
    def __init__(self, layout, page_manager, header_label) -> None:
        self.layout = layout
        self.page_manager = page_manager
        self.breadcrumb_label = header_label
        self.buttons = {}

    def register_button(self, name: str, button) -> None:
        """
        Maps a routing name to a specific sidebar UI button.
        """
        self.buttons[name] = button

    def show_page(self, page_name: str) -> None:
        """
        Switches active view tab in the page manager and highlights corresponding button.
        """
        if page_name not in self.buttons:
            return
            
        # 1. Update selection visual state of sidebar links
        for name, button in self.buttons.items():
            button.set_active(name == page_name)
            
        # 2. Transition active canvas in viewport frame
        self.page_manager.raise_page(page_name)
        
        # 3. Update top breadcrumbs
        self.breadcrumb_label.configure(text=f"System / {page_name}")
