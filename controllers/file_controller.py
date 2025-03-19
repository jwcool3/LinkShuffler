import json
import re
from tkinter import filedialog, messagebox
from models import Bookmark, Category
import os

class FileController:
    """
    Controller for handling file operations (loading/saving).
    """
    def __init__(self, app):
        """
        Initialize the file controller.
        
        Args:
            app: The main application instance
        """
        self.app = app
    
    def load_html_bookmarks(self):
        """
        Load bookmarks from an HTML file (typically exported from a browser).
        
        Returns:
            list: A list of Bookmark objects, or None if operation was canceled
        """
        file_path = filedialog.askopenfilename(
            title="Select Bookmark File",
            filetypes=[("HTML Files", "*.html"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return None  # User canceled
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
                # Extract links and titles using regex
                links_data = re.findall(r'<A HREF="(.*?)".*?>(.*?)</A>', content)
                
                if not links_data:
                    messagebox.showwarning(
                        "No Links Found",
                        "No links were found in the selected file."
                    )
                    return None
                
                # Create Bookmark objects
                bookmarks = []
                for url, title in links_data:
                    # Clean title and URL
                    title = title.strip()
                    url = url.strip()
                    bookmark = Bookmark(url=url, title=title)
                    bookmarks.append(bookmark)
                
                messagebox.showinfo(
                    "Success",
                    f"Loaded {len(bookmarks)} links from the file."
                )
                return bookmarks
                
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to read file: {str(e)}"
            )
            return None
    
    def save_data(self, filename=None):
        """
        Save bookmarks and categories to a JSON file.
        
        Args:
            filename (str, optional): The filename to save to. If None, a file dialog will be shown.
            
        Returns:
            bool: True if the save was successful, False otherwise
        """
        if not filename:
            filename = filedialog.asksaveasfilename(
                title="Save Bookmarks",
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
            )
            
            if not filename:  # User canceled
                return False
        
        try:
            # Prepare data for serialization
            data = {
                "bookmarks": [bookmark.to_dict() for bookmark in self.app.bookmarks],
                "categories": [category.to_dict() for category in self.app.categories]
            }
            
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4)
            
            messagebox.showinfo("Success", "Data saved successfully.")
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")
            return False
    
    def load_data(self, filename=None):
        """
        Load bookmarks and categories from a JSON file.
        
        Args:
            filename (str, optional): The filename to load from. If None, a file dialog will be shown.
            
        Returns:
            tuple: A tuple of (bookmarks, categories) if successful, or None if operation failed
        """
        if not filename:
            filename = filedialog.askopenfilename(
                title="Load Bookmarks",
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
            )
            
            if not filename:  # User canceled
                return None
        
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Load bookmarks
            bookmarks = [Bookmark.from_dict(bookmark_data) for bookmark_data in data.get("bookmarks", [])]
            
            # Load categories (requires bookmarks to be loaded first for references)
            categories = [
                Category.from_dict(category_data, bookmarks)
                for category_data in data.get("categories", [])
            ]
            
            messagebox.showinfo("Success", "Data loaded successfully.")
            return bookmarks, categories
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
            return None