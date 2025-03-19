import re
import tkinter as tk
from tkinter import messagebox, Toplevel
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    

class KeywordController:
    """
    Controller for handling keyword detection and auto-categorization.
    """
    def __init__(self, app):
        """
        Initialize the keyword controller.
        
        Args:
            app: The main application instance
        """
        self.app = app
    
    def extract_keywords(self):
        """
        Extract keywords from bookmark titles using TF-IDF.
        
        Returns:
            list: List of (keyword, score) tuples, or None if sklearn is not available
        """
        if not SKLEARN_AVAILABLE:
            messagebox.showwarning(
                "sklearn Not Available",
                "The scikit-learn package is required for keyword extraction. "
                "Please install it with 'pip install scikit-learn'."
            )
            return None
        
        if not self.app.bookmarks:
            messagebox.showwarning("No Bookmarks", "No bookmarks loaded to extract keywords.")
            return None
        
        # Get all titles
        titles = [bookmark.title for bookmark in self.app.bookmarks]
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            stop_words='english',  # Remove common English words
            ngram_range=(1, 2),    # Consider single words and pairs
            min_df=2,              # Ignore terms that appear in less than 2 documents
            max_df=0.8             # Ignore terms that appear in more than 80% of documents
        )
        
        try:
            # Compute TF-IDF
            tfidf_matrix = vectorizer.fit_transform(titles)
            feature_names = vectorizer.get_feature_names_out()
            
            # Get maximum TF-IDF score for each term
            max_tfidf = np.max(tfidf_matrix.toarray(), axis=0)
            
            # Get significant terms (above threshold)
            threshold = 0.1
            significant_terms = [
                (feature_names[i], max_tfidf[i])
                for i in range(len(feature_names))
                if max_tfidf[i] > threshold
            ]
            
            # Sort by score (descending)
            significant_terms.sort(key=lambda x: x[1], reverse=True)
            
            return significant_terms
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract keywords: {str(e)}")
            return None
    
    def show_keyword_dialog(self):
        """
        Show a dialog with extracted keywords for selection.
        
        Returns:
            list: List of selected keywords, or None if dialog was canceled
        """
        # Extract keywords
        keywords = self.extract_keywords()
        if not keywords:
            return None
        
        # Create dialog
        dialog = Toplevel(self.app.root)
        dialog.title("Detected Keywords")
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        # Instructions
        tk.Label(
            dialog,
            text="Select keywords to create categories (hold Ctrl for multiple selection):"
        ).pack(pady=10)
        
        # Listbox for keywords
        listbox = tk.Listbox(dialog, selectmode=tk.EXTENDED, width=60, height=20)
        listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = tk.Scrollbar(listbox)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)
        
        # Populate listbox
        for word, score in keywords:
            listbox.insert(tk.END, f"{word} (TF-IDF: {score:.3f})")
        
        # Result variable
        result = []
        
        # Button functions
        def on_ok():
            nonlocal result
            # Get selected indices
            selected_indices = listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("No Selection", "Please select at least one keyword.")
                return
            
            # Extract keywords from selection
            result = [listbox.get(i).split(' ')[0] for i in selected_indices]
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10, fill=tk.X)
        
        tk.Button(button_frame, text="OK", command=on_ok, width=10).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Cancel", command=on_cancel, width=10).pack(side=tk.RIGHT, padx=10)
        
        # Wait for dialog to close
        dialog.wait_window()
        
        return result if result else None
    
    def auto_categorize_bookmarks(self):
        """
        Automatically categorize bookmarks based on selected keywords.
        
        Returns:
            int: Number of bookmarks categorized, or None if operation was canceled
        """
        # Show keyword dialog
        selected_keywords = self.show_keyword_dialog()
        if not selected_keywords:
            return None
        
        # Create categories based on keywords
        link_controller = self.app.link_controller
        count = 0
        
        for keyword in selected_keywords:
            # Create category for each keyword
            category = link_controller._ensure_category_exists(keyword)
            
            # Find bookmarks matching keyword
            for bookmark in self.app.bookmarks:
                if keyword.lower() in bookmark.title.lower() and bookmark.category == "Uncategorized":
                    link_controller.update_bookmark(bookmark, category=keyword)
                    count += 1
        
        messagebox.showinfo(
            "Auto-Categorization Complete",
            f"Categorized {count} bookmarks based on selected keywords."
        )
        return count
    
    def extract_bookmark_keywords(self, bookmark):
        """
        Extract keywords from a single bookmark's title.
        
        Args:
            bookmark: The bookmark to extract keywords from
            
        Returns:
            list: List of keywords
        """
        if not bookmark.title:
            return []