import random
import webbrowser
import json
import os
from tkinter import simpledialog, messagebox
from models.bookmark import Bookmark
from models.category import Category
from datetime import datetime

class LinkController:
    """
    Controller for handling bookmark and category operations.
    """
    def __init__(self, app):
        """
        Initialize the link controller.
        
        Args:
            app: The main application instance
        """
        self.app = app
        self.shown_links = set()  # Track shown links for shuffle
        self.shuffled_bookmarks = []  # Current shuffled bookmarks
        self.shuffle_history_file = "shuffle_history.json"
        
        # Load shuffle history on startup
        self.load_shuffle_history()
    
    def create_bookmark(self, url, title, category="Uncategorized", rating=None):
        """
        Create a new bookmark or update an existing one.
        
        Args:
            url (str): The URL of the bookmark
            title (str): The title of the bookmark
            category (str, optional): The category name. Defaults to "Uncategorized".
            rating (int, optional): Rating from 1-5. Defaults to None.
            
        Returns:
            Bookmark: The newly created bookmark
        """
        # Check if bookmark already exists
        for bookmark in self.app.bookmarks:
            if bookmark.url == url:
                # Update existing bookmark but preserve date_added
                original_date = getattr(bookmark, 'date_added', datetime.now())
                bookmark.title = title
                bookmark.category = category
                if rating is not None:
                    bookmark.rating = rating
                # Preserve original date_added
                bookmark.date_added = original_date
                return bookmark
        
        # Create new bookmark
        bookmark = Bookmark(url=url, title=title, category=category, rating=rating)
        self.app.bookmarks.append(bookmark)
        
        # Add to category
        self._ensure_category_exists(category)
        for cat in self.app.categories:
            if cat.name == category:
                cat.add_bookmark(bookmark)
                break
        
        return bookmark
    
    def delete_bookmark(self, bookmark):
        """
        Delete a bookmark.
        
        Args:
            bookmark (Bookmark): The bookmark to delete
            
        Returns:
            bool: True if deleted, False otherwise
        """
        if bookmark in self.app.bookmarks:
            # Remove from categories
            for category in self.app.categories:
                if bookmark in category.bookmarks:
                    category.remove_bookmark(bookmark)
            
            # Remove from bookmarks list
            self.app.bookmarks.remove(bookmark)
            return True
        return False
    
    def update_bookmark(self, bookmark, **kwargs):
        """
        Update a bookmark with new values.
        
        Args:
            bookmark (Bookmark): The bookmark to update
            **kwargs: Attributes to update (title, url, category, rating)
            
        Returns:
            Bookmark: The updated bookmark
        """
        old_category = bookmark.category
        
        # Update bookmark attributes
        for key, value in kwargs.items():
            if hasattr(bookmark, key):
                setattr(bookmark, key, value)
        
        # Handle category change
        if "category" in kwargs and kwargs["category"] != old_category:
            # Remove from old category
            for category in self.app.categories:
                if category.name == old_category:
                    category.remove_bookmark(bookmark)
            
            # Add to new category
            new_category = kwargs["category"]
            self._ensure_category_exists(new_category)
            for category in self.app.categories:
                if category.name == new_category:
                    category.add_bookmark(bookmark)
        
        return bookmark
    
    def shuffle_bookmarks(self, count=None):
        """
        Shuffle bookmarks to get random ones that haven't been shown yet.
        
        Args:
            count (int, optional): Number of bookmarks to shuffle. If None, ask user.
            
        Returns:
            list: List of shuffled bookmarks
        """
        # Get all unshown bookmarks
        available_bookmarks = [b for b in self.app.bookmarks if b.url not in self.shown_links]
        
        # If all have been shown, reset
        if not available_bookmarks:
            messagebox.showinfo("No More Links", "All links have been shown. Resetting shown links.")
            self.shown_links.clear()
            available_bookmarks = self.app.bookmarks.copy()
        
        # Ask for count if not provided
        if count is None:
            count = simpledialog.askinteger(
                "Number of Links",
                "How many randomized links would you like to display?",
                minvalue=1,
                maxvalue=len(available_bookmarks)
            )
            if count is None:  # User canceled
                return []
        
        # Ensure count is valid
        count = min(count, len(available_bookmarks))
        
        # Use random.sample for better distribution and efficiency
        # This ensures uniform random selection without modifying the original list
        self.shuffled_bookmarks = random.sample(available_bookmarks, count)
        
        # Update shown links
        for bookmark in self.shuffled_bookmarks:
            self.shown_links.add(bookmark.url)
        
        # Save shuffle history
        self.save_shuffle_history()
        
        return self.shuffled_bookmarks
    
    def open_link(self, bookmark):
        """
        Open a bookmark URL in the web browser.
        
        Args:
            bookmark (Bookmark): The bookmark to open
        """
        if bookmark.url.startswith(('http://', 'https://')):
            webbrowser.open(bookmark.url)
        else:
            # Try adding https:// prefix if missing
            webbrowser.open('https://' + bookmark.url)
    
    def get_bookmarks_by_category(self, category_name):
        """
        Get all bookmarks in a specific category.
        
        Args:
            category_name (str): The category name
            
        Returns:
            list: List of bookmarks in the category
        """
        for category in self.app.categories:
            if category.name == category_name:
                return category.bookmarks
        return []
    
    def filter_bookmarks(self, search_term=None, category=None, min_rating=None):
        """
        Filter bookmarks based on criteria.
        
        Args:
            search_term (str, optional): Text to search in title or URL
            category (str, optional): Category to filter by
            min_rating (int, optional): Minimum rating to filter by
            
        Returns:
            list: Filtered list of bookmarks
        """
        result = self.app.bookmarks
        
        if search_term:
            search_term = search_term.lower()
            result = [b for b in result if search_term in b.title.lower() or search_term in b.url.lower()]
        
        if category and category != "All":
            result = [b for b in result if b.category == category]
        
        if min_rating is not None:
            result = [b for b in result if b.rating is not None and b.rating >= min_rating]
        
        return result
    
    def _ensure_category_exists(self, category_name):
        """
        Ensure a category exists, creating it if needed.
        
        Args:
            category_name (str): The category name
            
        Returns:
            Category: The category object
        """
        for category in self.app.categories:
            if category.name == category_name:
                return category
        
        # Create new category
        category = Category(category_name)
        self.app.categories.append(category)
        return category
    
    def save_shuffle_history(self):
        """
        Save the shuffle history (shown links) to a JSON file.
        """
        try:
            history_data = {
                "shown_links": list(self.shown_links),
                "total_bookmarks": len(self.app.bookmarks)
            }
            
            with open(self.shuffle_history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2)
        except Exception as e:
            print(f"Error saving shuffle history: {e}")
    
    def load_shuffle_history(self):
        """
        Load the shuffle history from a JSON file.
        """
        try:
            if os.path.exists(self.shuffle_history_file):
                with open(self.shuffle_history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
                    self.shown_links = set(history_data.get("shown_links", []))
        except Exception as e:
            print(f"Error loading shuffle history: {e}")
            self.shown_links = set()
    
    def reset_shuffle_history(self):
        """
        Reset the shuffle history (clear all shown links).
        
        Returns:
            bool: True if successful
        """
        self.shown_links.clear()
        self.save_shuffle_history()
        return True
    
    def get_shuffle_progress(self):
        """
        Get the current shuffle progress.
        
        Returns:
            tuple: (shown_count, total_count) representing shown and total bookmarks
        """
        total = len(self.app.bookmarks)
        shown = len([b for b in self.app.bookmarks if b.url in self.shown_links])
        return (shown, total)