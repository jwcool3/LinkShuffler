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
        
        # Setup UI
        self.main_window = MainWindow(self)
        
        # Load default JSON file if it exists
        default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bookmarks.json")
        if os.path.exists(default_path):
            self._load_default_data(default_path)
    
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