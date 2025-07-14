import tkinter as tk
from tkinter import ttk
import os

from controllers import FileController, LinkController, KeywordController
from models import Bookmark, Category
from views.main_window import MainWindow

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
        self.root.geometry("1000x700")
        
        # Setup application state
        self.bookmarks = []
        self.categories = []
        self._ensure_uncategorized_exists()
        
        # Setup controllers
        self.file_controller = FileController(self)
        self.link_controller = LinkController(self)
        self.keyword_controller = KeywordController(self)
        
        # Set main_window to None initially
        self.main_window = None
        
        # Auto-save configuration
        self.auto_save_enabled = True
        self.auto_save_interval = 300000  # 5 minutes in milliseconds
        self.auto_save_filename = "auto_save.json"
        
        # Setup UI
        self.main_window = MainWindow(self)
        
        # Load default JSON file if it exists
        default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bookmarks.json")
        if os.path.exists(default_path):
            self._load_default_data(default_path)
        
        # Start auto-save
        self.schedule_auto_save()
    
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

    def schedule_auto_save(self):
        """Schedule the next auto-save operation."""
        if self.auto_save_enabled:
            self.root.after(self.auto_save_interval, self.auto_save)
    
    def auto_save(self):
        """Perform auto-save operation."""
        try:
            # Only auto-save if there are bookmarks to save
            if self.bookmarks:
                self.file_controller.save_data(self.auto_save_filename)
                # Update status to show auto-save occurred
                if self.main_window:
                    self.main_window.update_status("Auto-saved bookmarks")
        except Exception as e:
            print(f"Auto-save failed: {e}")
        finally:
            # Schedule next auto-save
            self.schedule_auto_save()
    
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