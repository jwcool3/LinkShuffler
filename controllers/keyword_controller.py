import re
import tkinter as tk
from tkinter import messagebox, Toplevel
import tkinter.ttk as ttk
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
        Show an enhanced dialog with extracted keywords for selection.
        
        Returns:
            list: List of selected keywords, or None if dialog was canceled
        """
        # Extract keywords
        keywords = self.extract_keywords()
        if not keywords:
            return None

        # Create main dialog
        dialog = Toplevel(self.app.root)
        dialog.title("Smart Keyword Detection & Categorization")
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.geometry("900x700")
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450)
        y = (dialog.winfo_screenheight() // 2) - (350)
        dialog.geometry(f"900x700+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title and description
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(title_frame, text="Keyword Detection & Categorization", 
                 font=('Arial', 14, 'bold')).pack(anchor='w')
        ttk.Label(title_frame, text="Select keywords to create categories. Keywords are ranked by relevance (TF-IDF score).", 
                 font=('Arial', 10)).pack(anchor='w')
        
        # Control frame for sorting and filtering
        control_frame = ttk.LabelFrame(main_frame, text="Controls")
        control_frame.pack(fill='x', pady=(0, 10))
        
        # First row of controls
        control_row1 = ttk.Frame(control_frame)
        control_row1.pack(fill='x', padx=5, pady=5)
        
        # Sort options
        ttk.Label(control_row1, text="Sort by:").pack(side='left', padx=(0, 5))
        sort_var = tk.StringVar(value="score")
        sort_combo = ttk.Combobox(control_row1, textvariable=sort_var, width=15, state="readonly",
                                 values=["score", "alphabetical", "length", "frequency"])
        sort_combo.pack(side='left', padx=(0, 15))
        
        # Filter options
        ttk.Label(control_row1, text="Filter:").pack(side='left', padx=(0, 5))
        filter_var = tk.StringVar()
        filter_entry = ttk.Entry(control_row1, textvariable=filter_var, width=20)
        filter_entry.pack(side='left', padx=(0, 15))
        
        # Minimum score threshold
        ttk.Label(control_row1, text="Min Score:").pack(side='left', padx=(0, 5))
        min_score_var = tk.DoubleVar(value=0.1)
        min_score_spin = ttk.Spinbox(control_row1, from_=0.0, to=1.0, increment=0.05, 
                                    textvariable=min_score_var, width=8)
        min_score_spin.pack(side='left', padx=(0, 15))
        
        # Second row of controls
        control_row2 = ttk.Frame(control_frame)
        control_row2.pack(fill='x', padx=5, pady=(0, 5))
        
        # Selection buttons
        ttk.Button(control_row2, text="Select All", 
                  command=lambda: self._select_all_keywords(keyword_tree)).pack(side='left', padx=(0, 5))
        ttk.Button(control_row2, text="Select None", 
                  command=lambda: self._select_none_keywords(keyword_tree)).pack(side='left', padx=(0, 5))
        ttk.Button(control_row2, text="Select Top 10", 
                  command=lambda: self._select_top_keywords(keyword_tree, 10)).pack(side='left', padx=(0, 5))
        ttk.Button(control_row2, text="Select High Score (>0.3)", 
                  command=lambda: self._select_high_score_keywords(keyword_tree, 0.3)).pack(side='left', padx=(0, 15))
        
        # Auto-categorize options
        auto_frame = ttk.LabelFrame(control_frame, text="Auto-Categorization")
        auto_frame.pack(fill='x', padx=5, pady=5)
        
        auto_controls = ttk.Frame(auto_frame)
        auto_controls.pack(fill='x', padx=5, pady=5)
        
        group_similar_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(auto_controls, text="Group similar keywords", 
                       variable=group_similar_var).pack(side='left', padx=(0, 15))
        
        create_subcategories_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(auto_controls, text="Create subcategories", 
                       variable=create_subcategories_var).pack(side='left', padx=(0, 15))
        
        # Keyword tree frame
        tree_frame = ttk.LabelFrame(main_frame, text="Keywords")
        tree_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Create treeview with enhanced columns
        columns = ('score', 'frequency', 'category_suggestion', 'bookmark_count')
        keyword_tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings')
        
        # Configure headings
        keyword_tree.heading('#0', text='Keyword')
        keyword_tree.heading('score', text='TF-IDF Score')
        keyword_tree.heading('frequency', text='Frequency')
        keyword_tree.heading('category_suggestion', text='Suggested Category')
        keyword_tree.heading('bookmark_count', text='Bookmarks')
        
        # Configure column widths
        keyword_tree.column('#0', width=200)
        keyword_tree.column('score', width=100)
        keyword_tree.column('frequency', width=80)
        keyword_tree.column('category_suggestion', width=150)
        keyword_tree.column('bookmark_count', width=80)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=keyword_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=keyword_tree.xview)
        keyword_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        keyword_tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Preview frame
        preview_frame = ttk.LabelFrame(main_frame, text="Preview")
        preview_frame.pack(fill='x', pady=(0, 10))
        
        preview_text = tk.Text(preview_frame, height=4, wrap='word')
        preview_text.pack(fill='x', padx=5, pady=5)
        
        # Populate tree with keywords
        self._populate_keyword_tree(keyword_tree, keywords)
        
        # Bind events
        def on_sort_change(*args):
            self._sort_keyword_tree(keyword_tree, keywords, sort_var.get())
        
        def on_filter_change(*args):
            self._filter_keyword_tree(keyword_tree, keywords, filter_var.get(), min_score_var.get())
        
        def on_selection_change(*args):
            self._update_preview(keyword_tree, preview_text)
        
        sort_var.trace('w', on_sort_change)
        filter_var.trace('w', on_filter_change)
        min_score_var.trace('w', on_filter_change)
        keyword_tree.bind('<<TreeviewSelect>>', on_selection_change)
        
        # Result variable
        result = []
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Button functions
        def on_ok():
            nonlocal result
            selected_items = keyword_tree.selection()
            if not selected_items:
                messagebox.showwarning("No Selection", "Please select at least one keyword.")
                return
            
            # Extract keywords from selection
            result = []
            for item in selected_items:
                keyword = keyword_tree.item(item, 'text')
                if keyword:  # Make sure it's not empty
                    result.append(keyword)
            
            if not result:
                messagebox.showwarning("No Selection", "Please select at least one keyword.")
                return
            
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        def on_auto_categorize():
            # Get all keywords with high scores
            auto_keywords = []
            for item in keyword_tree.get_children():
                values = keyword_tree.item(item, 'values')
                if values and float(values[0]) > 0.2:  # Score > 0.2
                    keyword = keyword_tree.item(item, 'text')
                    auto_keywords.append(keyword)
            
            if auto_keywords:
                result[:] = auto_keywords
                dialog.destroy()
            else:
                messagebox.showinfo("No Keywords", "No keywords meet the auto-categorization criteria.")
        
        # Buttons
        ttk.Button(button_frame, text="Create Categories", command=on_ok).pack(side='left', padx=(0, 5))
        ttk.Button(button_frame, text="Auto-Categorize", command=on_auto_categorize).pack(side='left', padx=(0, 5))
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side='right')
        
        # Wait for dialog to close
        dialog.wait_window()
        
        return result if result else None
    
    def _populate_keyword_tree(self, tree, keywords):
        """Populate the keyword tree with data."""
        for keyword, score in keywords:
            # Calculate frequency (how many bookmarks contain this keyword)
            frequency = sum(1 for b in self.app.bookmarks if keyword.lower() in b.title.lower())
            
            # Suggest category name
            category_suggestion = self._suggest_category_name(keyword)
            
            # Count bookmarks that would be affected
            bookmark_count = sum(1 for b in self.app.bookmarks 
                               if keyword.lower() in b.title.lower() and b.category == "Uncategorized")
            
            tree.insert('', 'end', text=keyword, values=(
                f"{score:.3f}",
                frequency,
                category_suggestion,
                bookmark_count
            ))
    
    def _suggest_category_name(self, keyword):
        """Suggest a category name based on keyword."""
        # Simple capitalization and cleanup
        suggestion = keyword.replace('_', ' ').title()
        
        # Check if it's an adult keyword and suggest appropriate category
        adult_keywords = ['adult', 'xxx', 'porn', 'sex', 'nsfw', 'mature', 'explicit']
        if any(adult_kw in keyword.lower() for adult_kw in adult_keywords):
            suggestion = f"Adult - {suggestion}"
        
        return suggestion
    
    def _sort_keyword_tree(self, tree, keywords, sort_by):
        """Sort the keyword tree by the specified criteria."""
        # Clear current items
        for item in tree.get_children():
            tree.delete(item)
        
        # Sort keywords
        if sort_by == "alphabetical":
            sorted_keywords = sorted(keywords, key=lambda x: x[0].lower())
        elif sort_by == "length":
            sorted_keywords = sorted(keywords, key=lambda x: len(x[0]))
        elif sort_by == "frequency":
            sorted_keywords = sorted(keywords, key=lambda x: sum(1 for b in self.app.bookmarks 
                                                               if x[0].lower() in b.title.lower()), reverse=True)
        else:  # score
            sorted_keywords = sorted(keywords, key=lambda x: x[1], reverse=True)
        
        # Repopulate tree
        self._populate_keyword_tree(tree, sorted_keywords)
    
    def _filter_keyword_tree(self, tree, keywords, filter_text, min_score):
        """Filter the keyword tree based on text and minimum score."""
        # Clear current items
        for item in tree.get_children():
            tree.delete(item)
        
        # Filter keywords
        filtered_keywords = []
        for keyword, score in keywords:
            if score >= min_score:
                if not filter_text or filter_text.lower() in keyword.lower():
                    filtered_keywords.append((keyword, score))
        
        # Repopulate tree
        self._populate_keyword_tree(tree, filtered_keywords)
    
    def _select_all_keywords(self, tree):
        """Select all keywords in the tree."""
        tree.selection_set(tree.get_children())
    
    def _select_none_keywords(self, tree):
        """Deselect all keywords in the tree."""
        tree.selection_remove(tree.get_children())
    
    def _select_top_keywords(self, tree, count):
        """Select the top N keywords by score."""
        children = tree.get_children()
        if children:
            tree.selection_set(children[:min(count, len(children))])
    
    def _select_high_score_keywords(self, tree, min_score):
        """Select keywords with score above threshold."""
        selected = []
        for item in tree.get_children():
            values = tree.item(item, 'values')
            if values and float(values[0]) > min_score:
                selected.append(item)
        
        if selected:
            tree.selection_set(selected)
    
    def _update_preview(self, tree, preview_text):
        """Update the preview text with selected keywords."""
        selected_items = tree.selection()
        
        preview_text.delete(1.0, tk.END)
        
        if not selected_items:
            preview_text.insert(tk.END, "No keywords selected.")
            return
        
        preview_text.insert(tk.END, f"Selected {len(selected_items)} keywords:\n\n")
        
        categories_preview = {}
        total_bookmarks = 0
        
        for item in selected_items:
            keyword = tree.item(item, 'text')
            values = tree.item(item, 'values')
            
            if values:
                score = float(values[0])
                bookmark_count = int(values[3])
                category = values[2]
                
                if category not in categories_preview:
                    categories_preview[category] = []
                
                categories_preview[category].append((keyword, bookmark_count))
                total_bookmarks += bookmark_count
        
        preview_text.insert(tk.END, f"Will create {len(categories_preview)} categories affecting {total_bookmarks} bookmarks:\n\n")
        
        for category, keywords in categories_preview.items():
            keyword_list = ", ".join([f"{kw} ({count})" for kw, count in keywords])
            preview_text.insert(tk.END, f"• {category}: {keyword_list}\n")
        
        preview_text.config(state='disabled')
    
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
            
        # Simple keyword extraction for a single title
        title = bookmark.title.lower()
        
        # Remove common stop words
        stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'is', 'are', 'on', 'in', 'to', 'for', 'with', 'by', 'at', 'from'}
        
        # Clean and tokenize
        title = re.sub(r'[^\w\s]', ' ', title)  # Replace punctuation with space
        words = [w for w in title.split() if w not in stop_words and len(w) > 2]
        
        # Return unique words
        return list(set(words))
    
    def suggest_category(self, bookmark):
        """
        Suggest a category for a bookmark based on its title.
        
        Args:
            bookmark: The bookmark to suggest a category for
            
        Returns:
            str: Suggested category name, or None if no suggestion
        """
        # Extract keywords
        keywords = self.extract_bookmark_keywords(bookmark)
        if not keywords:
            return None
        
        # Get existing categories
        categories = [cat.name for cat in self.app.categories if cat.name != "Uncategorized"]
        if not categories:
            return None
        
        # Check if any keyword matches an existing category
        for keyword in keywords:
            for category in categories:
                if keyword.lower() in category.lower() or category.lower() in keyword.lower():
                    return category
        
        # If no direct match, suggest the most common category among similar bookmarks
        similar_bookmarks = []
        for b in self.app.bookmarks:
            if b != bookmark and b.category != "Uncategorized":
                b_keywords = self.extract_bookmark_keywords(b)
                # Check for keyword overlap
                if any(kw in b_keywords for kw in keywords):
                    similar_bookmarks.append(b)
        
        if similar_bookmarks:
            # Count categories of similar bookmarks
            category_counts = {}
            for b in similar_bookmarks:
                category_counts[b.category] = category_counts.get(b.category, 0) + 1
            
            # Return most common category
            if category_counts:
                return max(category_counts.items(), key=lambda x: x[1])[0]
        
        return None