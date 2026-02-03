import json
import re
import csv
import os
from datetime import datetime
from tkinter import filedialog, messagebox
from models.bookmark import Bookmark
from models.category import Category
from difflib import SequenceMatcher
import threading
from urllib.parse import urlparse
from collections import defaultdict

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
    
    def import_html_bookmarks(self):
        """
        Import bookmarks from an HTML file.
        
        Returns:
            list: List of Bookmark objects, or None if operation failed
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
                
                # Extract links, titles, and dates using regex
                # Updated regex to capture ADD_DATE attribute
                bookmark_pattern = r'<A HREF="(.*?)"(?:.*?ADD_DATE="(\d+)")?.*?>(.*?)</A>'
                links_data = re.findall(bookmark_pattern, content, re.IGNORECASE | re.DOTALL)
                
                if not links_data:
                    messagebox.showwarning(
                        "No Links Found",
                        "No links were found in the selected file."
                    )
                    return None
                
                # Create Bookmark objects
                bookmarks = []
                for url, add_date, title in links_data:
                    # Clean title and URL
                    title = title.strip()
                    url = url.strip()
                    
                    # Create bookmark
                    bookmark = Bookmark(url=url, title=title)
                    
                    # Set the original date if ADD_DATE is present
                    if add_date:
                        try:
                            # Convert Unix timestamp to datetime
                            timestamp = int(add_date)
                            bookmark.date_added = datetime.fromtimestamp(timestamp)
                        except (ValueError, OSError):
                            # If conversion fails, keep the default date_added from constructor
                            pass
                    
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

    def find_duplicates(self, progress_callback=None):
        """
        Find potential duplicate bookmarks based on URL and title similarity.
        Uses optimized algorithms and threading to prevent UI freezing.
        
        Args:
            progress_callback: Optional callback function to report progress
        
        Returns:
            list: List of tuples containing potential duplicate pairs
        """
        bookmarks = self.app.bookmarks
        if not bookmarks:
            return []
        
        duplicates = []
        
        if progress_callback:
            progress_callback(10, "Analyzing bookmarks...")
        
        # Phase 1: Find exact URL matches (very fast)
        url_groups = defaultdict(list)
        for bookmark in bookmarks:
            normalized_url = self._normalize_url(bookmark.url)
            url_groups[normalized_url].append(bookmark)
        
        # Add exact URL duplicates
        for url, bookmark_list in url_groups.items():
            if len(bookmark_list) > 1:
                for i in range(len(bookmark_list)):
                    for j in range(i + 1, len(bookmark_list)):
                        duplicates.append((bookmark_list[i], bookmark_list[j], "Exact URL match"))
        
        if progress_callback:
            progress_callback(40, f"Found {len(duplicates)} exact URL matches...")
        
        # Phase 2: Find very similar titles (much more conservative)
        # Only look for titles that are nearly identical
        title_duplicates = []
        processed_pairs = set()  # Track processed pairs to avoid duplicates
        
        # Add all URL pairs to processed_pairs to avoid checking them again
        for url, bookmark_list in url_groups.items():
            if len(bookmark_list) > 1:
                for i in range(len(bookmark_list)):
                    for j in range(i + 1, len(bookmark_list)):
                        pair_key = tuple(sorted([bookmark_list[i].url, bookmark_list[j].url]))
                        processed_pairs.add(pair_key)
        
        # Group bookmarks by normalized titles for more accurate matching
        title_groups = defaultdict(list)
        for bookmark in bookmarks:
            if bookmark.title:
                # Use first 10 characters and remove common words for better grouping
                normalized_title = self._normalize_title(bookmark.title)
                if len(normalized_title) >= 5:  # Only group titles with meaningful content
                    key = normalized_title[:10].lower()
                    title_groups[key].append(bookmark)
        
        if progress_callback:
            progress_callback(60, "Checking for similar titles...")
        
        # Only compare bookmarks within the same title group
        for group_bookmarks in title_groups.values():
            if len(group_bookmarks) < 2:
                continue
                
            for i in range(len(group_bookmarks)):
                for j in range(i + 1, len(group_bookmarks)):
                    bookmark1, bookmark2 = group_bookmarks[i], group_bookmarks[j]
                    
                    # Skip if already processed as URL duplicate
                    pair_key = tuple(sorted([bookmark1.url, bookmark2.url]))
                    if pair_key in processed_pairs:
                        continue
                    processed_pairs.add(pair_key)
                    
                    # Skip if URLs are the same (already handled in Phase 1)
                    if self._normalize_url(bookmark1.url) == self._normalize_url(bookmark2.url):
                        continue
                    
                    # More conservative length check
                    title1_len = len(bookmark1.title)
                    title2_len = len(bookmark2.title)
                    if abs(title1_len - title2_len) > min(title1_len, title2_len) * 0.2:
                        continue
                    
                    # Calculate similarity with higher threshold
                    similarity = self._fast_similarity_score(bookmark1.title, bookmark2.title)
                    if similarity > 0.95:  # Much higher threshold for title similarity
                        title_duplicates.append((bookmark1, bookmark2, f"Very similar title ({similarity:.3f})"))
        
        duplicates.extend(title_duplicates)
        
        if progress_callback:
            progress_callback(80, f"Found {len(title_duplicates)} similar titles...")
        
        # Phase 3: Find exact duplicates with minor URL variations (very conservative)
        url_variation_duplicates = self._find_url_variation_duplicates(bookmarks, processed_pairs)
        duplicates.extend(url_variation_duplicates)
        
        if progress_callback:
            progress_callback(100, f"Found {len(duplicates)} potential duplicates")
        
        return duplicates
    
    def _normalize_title(self, title):
        """
        Normalize title for better comparison by removing common noise.
        
        Args:
            title (str): Title to normalize
            
        Returns:
            str: Normalized title
        """
        if not title:
            return ""
        
        # Remove common noise words and characters
        title = title.lower()
        title = re.sub(r'[^\w\s]', ' ', title)  # Replace punctuation with spaces
        title = re.sub(r'\s+', ' ', title)  # Normalize whitespace
        title = title.strip()
        
        # Remove very common words that don't help with matching
        noise_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = title.split()
        filtered_words = [word for word in words if word not in noise_words and len(word) > 2]
        
        return ' '.join(filtered_words)
    
    def _normalize_url(self, url):
        """
        Normalize URL for comparison by removing common variations.
        
        Args:
            url (str): URL to normalize
            
        Returns:
            str: Normalized URL
        """
        if not url:
            return ""
        
        # Remove common protocol variations
        url = url.lower()
        url = re.sub(r'^https?://', '', url)
        url = re.sub(r'^www\.', '', url)
        
        # Remove trailing slashes
        url = url.rstrip('/')
        
        # Remove common tracking parameters but keep important query parameters
        # Only remove very common tracking parameters
        url = re.sub(r'[?&]utm_[^&]*', '', url)
        url = re.sub(r'[?&]fbclid=[^&]*', '', url)
        url = re.sub(r'[?&]gclid=[^&]*', '', url)
        
        return url
    
    def _fast_similarity_score(self, text1, text2):
        """
        Calculate similarity score with optimizations for performance.
        
        Args:
            text1 (str): First text string
            text2 (str): Second text string
            
        Returns:
            float: Similarity score between 0 and 1
        """
        if not text1 or not text2:
            return 0.0
        
        # Quick exact match check
        if text1.lower() == text2.lower():
            return 1.0
        
        # Quick length ratio check
        len_ratio = min(len(text1), len(text2)) / max(len(text1), len(text2))
        if len_ratio < 0.5:  # If one is less than half the length of the other
            return 0.0
        
        # Use SequenceMatcher for detailed comparison
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def _find_url_variation_duplicates(self, bookmarks, processed_pairs):
        """
        Find bookmarks that are likely the same content with minor URL variations.
        This is much more conservative than the previous domain duplicate logic.
        
        Args:
            bookmarks: List of bookmarks to check
            processed_pairs: Set of already processed bookmark pairs
            
        Returns:
            list: List of URL variation duplicate tuples
        """
        url_variation_duplicates = []
        
        # Group bookmarks by domain and base path
        domain_path_groups = defaultdict(list)
        for bookmark in bookmarks:
            try:
                parsed = urlparse(bookmark.url)
                domain = parsed.netloc.lower()
                domain = re.sub(r'^www\.', '', domain)
                
                # Get base path (remove query parameters and fragments)
                base_path = parsed.path.rstrip('/')
                
                # Only group if there's a meaningful base path
                if base_path and len(base_path) > 1:
                    key = f"{domain}{base_path}"
                    domain_path_groups[key].append(bookmark)
            except:
                continue  # Skip invalid URLs
        
        # Check for URL variations within the same domain/path group
        for group_bookmarks in domain_path_groups.values():
            if len(group_bookmarks) < 2:
                continue
                
            for i in range(len(group_bookmarks)):
                for j in range(i + 1, len(group_bookmarks)):
                    bookmark1, bookmark2 = group_bookmarks[i], group_bookmarks[j]
                    
                    # Skip if already processed
                    pair_key = tuple(sorted([bookmark1.url, bookmark2.url]))
                    if pair_key in processed_pairs:
                        continue
                    
                    try:
                        parsed1 = urlparse(bookmark1.url)
                        parsed2 = urlparse(bookmark2.url)
                        
                        # Check if they have the same domain and path but different query parameters
                        if (parsed1.netloc.lower() == parsed2.netloc.lower() and 
                            parsed1.path == parsed2.path and
                            parsed1.query != parsed2.query):
                            
                            # Only consider it a duplicate if the titles are also very similar
                            title_similarity = self._fast_similarity_score(bookmark1.title, bookmark2.title)
                            if title_similarity > 0.9:
                                url_variation_duplicates.append((bookmark1, bookmark2, f"Same page, different parameters ({title_similarity:.3f})"))
                    except:
                        continue  # Skip invalid URLs
        
        return url_variation_duplicates
    
    def find_duplicates_async(self, callback):
        """
        Find duplicates asynchronously to prevent UI freezing.
        
        Args:
            callback: Function to call with results when complete
        """
        def progress_update(percent, message):
            # Update UI in main thread
            self.app.root.after(0, lambda: self._update_progress(percent, message))
        
        def worker():
            try:
                duplicates = self.find_duplicates(progress_callback=progress_update)
                # Call callback in main thread
                self.app.root.after(0, lambda: callback(duplicates))
            except Exception as e:
                # Handle errors in main thread
                self.app.root.after(0, lambda: callback(None, str(e)))
        
        # Start worker thread
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def _update_progress(self, percent, message):
        """Update progress in the UI (to be overridden by UI components)."""
        pass

    def similarity_score(self, text1, text2):
        """
        Calculate similarity score between two text strings.
        
        Args:
            text1 (str): First text string
            text2 (str): Second text string
            
        Returns:
            float: Similarity score between 0 and 1
        """
        return self._fast_similarity_score(text1, text2)

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