import json
import re
import csv
import os
from tkinter import filedialog, messagebox
from models import Bookmark, Category
from difflib import SequenceMatcher

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

    def export_to_csv(self, bookmarks=None, filename=None):
        """
        Export bookmarks to CSV format.
        
        Args:
            bookmarks (list, optional): List of bookmarks to export. If None, exports all bookmarks.
            filename (str, optional): The filename to save to. If None, a file dialog will be shown.
            
        Returns:
            bool: True if the export was successful, False otherwise
        """
        if bookmarks is None:
            bookmarks = self.app.bookmarks
        
        if not bookmarks:
            messagebox.showwarning("No Bookmarks", "No bookmarks to export.")
            return False
        
        if not filename:
            filename = filedialog.asksaveasfilename(
                title="Export Bookmarks to CSV",
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
            )
            
            if not filename:  # User canceled
                return False
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Title', 'URL', 'Category', 'Rating', 'Keywords'])
                
                for bookmark in bookmarks:
                    writer.writerow([
                        bookmark.title,
                        bookmark.url,
                        bookmark.category,
                        bookmark.rating if bookmark.rating else '',
                        ','.join(bookmark.keywords) if bookmark.keywords else ''
                    ])
            
            messagebox.showinfo("Success", f"Exported {len(bookmarks)} bookmarks to CSV.")
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export to CSV: {str(e)}")
            return False

    def import_from_csv(self, filename=None):
        """
        Import bookmarks from CSV format.
        
        Args:
            filename (str, optional): The filename to import from. If None, a file dialog will be shown.
            
        Returns:
            list: List of imported bookmarks, or None if operation failed
        """
        if not filename:
            filename = filedialog.askopenfilename(
                title="Import Bookmarks from CSV",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
            )
            
            if not filename:  # User canceled
                return None
        
        try:
            bookmarks = []
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                header = next(reader, None)  # Skip header row
                
                if not header:
                    messagebox.showwarning("Invalid CSV", "CSV file appears to be empty.")
                    return None
                
                for row in reader:
                    if len(row) >= 2:  # At least title and URL
                        title = row[0].strip()
                        url = row[1].strip()
                        category = row[2].strip() if len(row) > 2 and row[2].strip() else "Uncategorized"
                        rating = None
                        keywords = []
                        
                        # Parse rating
                        if len(row) > 3 and row[3].strip():
                            try:
                                rating = int(row[3].strip())
                            except ValueError:
                                pass
                        
                        # Parse keywords
                        if len(row) > 4 and row[4].strip():
                            keywords = [k.strip() for k in row[4].split(',') if k.strip()]
                        
                        bookmark = Bookmark(url=url, title=title, category=category, rating=rating)
                        bookmark.keywords = keywords
                        bookmarks.append(bookmark)
            
            messagebox.showinfo("Success", f"Imported {len(bookmarks)} bookmarks from CSV.")
            return bookmarks
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import from CSV: {str(e)}")
            return None

    def find_duplicates(self):
        """
        Find potential duplicate bookmarks based on URL and title similarity.
        
        Returns:
            list: List of tuples containing potential duplicate pairs
        """
        duplicates = []
        bookmarks = self.app.bookmarks
        
        for i, bookmark1 in enumerate(bookmarks):
            for bookmark2 in bookmarks[i+1:]:
                # Check for exact URL match
                if bookmark1.url == bookmark2.url:
                    duplicates.append((bookmark1, bookmark2, "Exact URL match"))
                # Check for title similarity
                elif self.similarity_score(bookmark1.title, bookmark2.title) > 0.8:
                    duplicates.append((bookmark1, bookmark2, "Similar title"))
        
        return duplicates

    def similarity_score(self, text1, text2):
        """
        Calculate similarity score between two text strings.
        
        Args:
            text1 (str): First text string
            text2 (str): Second text string
            
        Returns:
            float: Similarity score between 0 and 1
        """
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

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
            
            # Only show success message if not auto-saving
            if not filename.endswith("auto_save.json"):
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