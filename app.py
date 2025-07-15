import tkinter as tk
from tkinter import ttk
import os

from controllers import FileController, LinkController, KeywordController
from controllers.enhanced_keyword_controller import EnhancedKeywordController
from models import Bookmark, Category
from views.main_window import MainWindow
from utils.config_manager import ConfigManager

class BookmarkShufflerApp:
    """
    Main application class for BookmarkShuffler.
    """
    def __init__(self, root):
        """
        Initialize the application.
        
        Args:
            root: The tkinter root window
        """
        self.root = root
        self.root.title("Bookmark Manager")
        
        # Initialize config manager
        self.config_manager = ConfigManager()
        self.config = self.config_manager.config
        
        # Apply window settings from config
        self.root.geometry(f"{self.config.window_width}x{self.config.window_height}")
        if self.config.window_maximized:
            self.root.state('zoomed')
        
        # Set theme
        try:
            style = tk.ttk.Style()
            style.theme_use(self.config.theme)
        except tk.TclError:
            # Fallback to default theme if configured theme is not available
            pass
        
        # Setup application state
        self.bookmarks = []
        self.categories = []
        self._ensure_uncategorized_exists()
        
        # Setup controllers
        self.file_controller = FileController(self)
        self.link_controller = LinkController(self)
        self.keyword_controller = KeywordController(self)
        self.enhanced_keyword_controller = EnhancedKeywordController(self)
        
        # Set main_window to None initially
        self.main_window = None
        
        # Initialize main window with config
        self.main_window = MainWindow(self)
        
        # Setup auto-save if enabled
        if self.config.auto_save_enabled:
            self.setup_auto_save()
        
        # Bind window close event to save config
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Load default JSON file if it exists
        default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bookmarks.json")
        if os.path.exists(default_path):
            self._load_default_data(default_path)
        
        # Start auto-save
        # self.schedule_auto_save() # This line is removed as per the new_code, as auto-save is now handled by setup_auto_save
    
    def setup_auto_save(self):
        """Setup auto-save functionality"""
        def auto_save():
            if hasattr(self.main_window, 'manage_tab'):
                # Save current data
                self.file_controller.save_data(self.config.auto_save_filename)
            
            # Schedule next auto-save
            self.root.after(self.config.auto_save_interval * 1000, auto_save)
        
        # Start auto-save timer
        self.root.after(self.config.auto_save_interval * 1000, auto_save)
    
    def on_closing(self):
        """Handle application closing"""
        # Save window state
        if self.root.state() == 'zoomed':
            self.config.window_maximized = True
        else:
            self.config.window_maximized = False
            self.config.window_width = self.root.winfo_width()
            self.config.window_height = self.root.winfo_height()
        
        # Save config
        self.config_manager.save_config()
        
        # Close application
        self.root.destroy()
    
    def run(self):
        """Run the application."""
        self.root.mainloop()
    
    def _ensure_uncategorized_exists(self):
        """Ensure the 'Uncategorized' category exists."""
        for category in self.categories:
            if category.name == "Uncategorized":
                return category
        
        # Create 'Uncategorized' category
        category = Category("Uncategorized")
        self.categories.append(category)
        return category
    
    def _load_default_data(self, file_path):
        """
        Load data from the default JSON file.
        
        Args:
            file_path: Path to the default JSON file
        """
        result = self.file_controller.load_data(file_path)
        if result:
            self.bookmarks, self.categories = result
            self._ensure_uncategorized_exists()
            self.main_window.update_ui()

    # schedule_auto_save and auto_save methods are removed as per the new_code, as auto-save is now handled by setup_auto_save
    
    def toggle_auto_save(self):
        """Toggle auto-save functionality on/off."""
        self.auto_save_enabled = not self.auto_save_enabled
        if self.auto_save_enabled:
            self.schedule_auto_save()
            if self.main_window:
                self.main_window.update_status("Auto-save enabled")
        else:
            if self.main_window:
                self.main_window.update_status("Auto-save disabled")
    
    def set_auto_save_interval(self, minutes):
        """
        Set the auto-save interval.
        
        Args:
            minutes (int): Auto-save interval in minutes
        """
        self.auto_save_interval = minutes * 60 * 1000  # Convert to milliseconds
        if self.main_window:
            self.main_window.update_status(f"Auto-save interval set to {minutes} minutes")