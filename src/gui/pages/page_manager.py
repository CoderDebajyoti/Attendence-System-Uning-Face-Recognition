# ==============================================================================
# Face Recognition Attendance System - Page Manager
# ==============================================================================

class PageManager:
    """
    Manages page caching and lazy instantiation. Avoids loading heavy 
    view architectures on bootstrap by instantiating frames only when requested.
    """
    def __init__(self, page_container, controller) -> None:
        self.container = page_container
        self.controller = controller
        self.pages = {}
        self.page_classes = {}

    def register_page(self, name: str, page_class) -> None:
        """
        Registers a routing string to a specific page view class.
        """
        self.page_classes[name] = page_class

    def raise_page(self, name: str) -> None:
        """
        Lifts the requested page layout to the top of the viewport stack.
        Creates it on the fly if it hasn't been instantiated yet.
        """
        if name not in self.pages and name in self.page_classes:
            page_class = self.page_classes[name]
            # Lazy initialize the page view frame
            frame = page_class(parent=self.container, controller=self.controller)
            frame.grid(row=0, column=0, sticky="nsew")
            self.pages[name] = frame
            
        if name in self.pages:
            self.pages[name].tkraise()
