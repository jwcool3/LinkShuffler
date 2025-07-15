import re
import tkinter as tk
from tkinter import messagebox, Toplevel
import tkinter.ttk as ttk
from collections import defaultdict
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
        self._keyword_cache = {}  # Cache for expensive calculations
        self._last_bookmark_count = 0
    
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
        
        # Check cache validity
        current_count = len(self.app.bookmarks)
        if (current_count == self._last_bookmark_count and 
            'keywords' in self._keyword_cache):
            return self._keyword_cache['keywords']
        
        # Get all titles
        titles = [bookmark.title for bookmark in self.app.bookmarks]
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            stop_words='english',  # Remove common English words
            ngram_range=(1, 2),    # Consider single words and pairs
            min_df=3,              # Include terms that appear in at least 3 documents (was 1)
            max_df=0.7,            # Ignore terms that appear in more than 70% of documents (was 0.9)
            max_features=1000,     # Limit to top 1000 features for better performance
            token_pattern=r'(?u)\b\w\w+\b'  # Only include words with 2+ characters
        )
        
        try:
            # Fit and transform the titles
            tfidf_matrix = vectorizer.fit_transform(titles)
            
            # Get feature names (keywords)
            feature_names = vectorizer.get_feature_names_out()
            
            # Calculate mean TF-IDF score for each keyword
            mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
            
            # Create keyword-score pairs
            keywords = [(feature_names[i], mean_scores[i]) 
                       for i in range(len(feature_names))]
            
            # Sort by score (descending)
            keywords.sort(key=lambda x: x[1], reverse=True)
            
            # Cache results
            self._keyword_cache['keywords'] = keywords
            self._last_bookmark_count = current_count
            
            return keywords
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract keywords: {str(e)}")
            return None
    
    def _calculate_keyword_metrics(self, keywords):
        """
        Pre-calculate all metrics for keywords to avoid repeated calculations.
        
        Args:
            keywords: List of (keyword, score) tuples
            
        Returns:
            dict: Dictionary with keyword metrics
        """
        if 'metrics' in self._keyword_cache:
            return self._keyword_cache['metrics']
        
        metrics = {}
        
        # Pre-calculate all metrics in batch
        for keyword, score in keywords:
            # For single words, search as-is
            # For multi-word phrases, try different matching strategies
            if ' ' in keyword:
                # Multi-word keyword - try exact match first, then word-by-word
                frequency = sum(1 for b in self.app.bookmarks 
                              if keyword.lower() in b.title.lower())
                
                # If no exact matches, try matching all words in the phrase
                if frequency == 0:
                    words = keyword.lower().split()
                    frequency = sum(1 for b in self.app.bookmarks 
                                  if all(word in b.title.lower() for word in words))
            else:
                # Single word keyword
                frequency = sum(1 for b in self.app.bookmarks 
                              if keyword.lower() in b.title.lower())
            
            category_suggestion = self._suggest_category_name(keyword)
            
            # Calculate bookmark count for uncategorized bookmarks
            if ' ' in keyword:
                # Multi-word keyword
                bookmark_count = sum(1 for b in self.app.bookmarks 
                                   if keyword.lower() in b.title.lower() and 
                                   b.category == "Uncategorized")
                
                # If no exact matches, try matching all words in the phrase
                if bookmark_count == 0:
                    words = keyword.lower().split()
                    bookmark_count = sum(1 for b in self.app.bookmarks 
                                       if all(word in b.title.lower() for word in words) and 
                                       b.category == "Uncategorized")
            else:
                # Single word keyword
                bookmark_count = sum(1 for b in self.app.bookmarks 
                                   if keyword.lower() in b.title.lower() and 
                                   b.category == "Uncategorized")
            
            metrics[keyword] = {
                'score': score,
                'frequency': frequency,
                'category_suggestion': category_suggestion,
                'bookmark_count': bookmark_count
            }
        
        self._keyword_cache['metrics'] = metrics
        return metrics
    
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

        # Pre-calculate metrics
        metrics = self._calculate_keyword_metrics(keywords)

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
        min_score_var = tk.DoubleVar(value=0.01)  # Changed from 0.1 to 0.01
        min_score_spin = ttk.Spinbox(control_row1, from_=0.0, to=1.0, increment=0.01, 
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
        
        # Store original data and current display data
        self._original_keywords = keywords
        self._current_keywords = keywords.copy()
        self._metrics = metrics
        
        # Populate tree with keywords
        self._populate_keyword_tree_optimized(keyword_tree, keywords, metrics)
        
        # Bind events with optimized handlers
        def on_sort_change(*args):
            self._sort_and_filter_keywords(keyword_tree, sort_var.get(), filter_var.get(), min_score_var.get())
        
        def on_filter_change(*args):
            self._sort_and_filter_keywords(keyword_tree, sort_var.get(), filter_var.get(), min_score_var.get())
        
        def on_selection_change(*args):
            self._update_preview(keyword_tree, preview_text)
        
        # Use after_idle to prevent excessive updates
        def debounced_update(*args):
            dialog.after_idle(lambda: self._sort_and_filter_keywords(keyword_tree, sort_var.get(), filter_var.get(), min_score_var.get()))
        
        sort_var.trace('w', on_sort_change)
        filter_var.trace('w', debounced_update)
        min_score_var.trace('w', debounced_update)
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
            keywords = []
            for item in selected_items:
                keyword = keyword_tree.item(item, 'text')
                if keyword:  # Make sure it's not empty
                    keywords.append(keyword)
            
            if not keywords:
                messagebox.showwarning("No Selection", "Please select at least one keyword.")
                return
            
            # Return keywords along with settings
            result = (keywords, group_similar_var.get(), create_subcategories_var.get())
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        def on_auto_categorize():
            nonlocal result
            # Get all keywords with high scores
            auto_keywords = []
            for item in keyword_tree.get_children():
                values = keyword_tree.item(item, 'values')
                if values and float(values[0]) > 0.2:  # Score > 0.2
                    keyword = keyword_tree.item(item, 'text')
                    auto_keywords.append(keyword)
            
            if auto_keywords:
                # Return keywords along with settings
                result = (auto_keywords, group_similar_var.get(), create_subcategories_var.get())
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
    
    def _populate_keyword_tree_optimized(self, tree, keywords, metrics):
        """Populate the keyword tree with pre-calculated data."""
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
        
        # Use batch insertion for better performance
        items_to_insert = []
        for keyword, score in keywords:
            metric = metrics[keyword]
            items_to_insert.append((keyword, (
                f"{metric['score']:.3f}",
                metric['frequency'],
                metric['category_suggestion'],
                metric['bookmark_count']
            )))
        
        # Insert all items at once
        for keyword, values in items_to_insert:
            tree.insert('', 'end', text=keyword, values=values)
    
    def _sort_and_filter_keywords(self, tree, sort_by, filter_text, min_score):
        """Combined sort and filter operation for better performance."""
        # Safety check: ensure metrics are available
        if not hasattr(self, '_metrics') or not self._metrics:
            self._metrics = self._calculate_keyword_metrics(self._original_keywords)
        
        # Start with original keywords
        filtered_keywords = []
        
        # Apply filters first
        for keyword, score in self._original_keywords:
            # Safety check for individual metric
            if keyword not in self._metrics:
                continue
                
            metric = self._metrics[keyword]
            
            # Apply score filter
            if metric['score'] < min_score:
                continue
            
            # Apply text filter
            if filter_text and filter_text.lower() not in keyword.lower():
                continue
            
            filtered_keywords.append((keyword, score))
        
        # Apply sorting
        if sort_by == "alphabetical":
            filtered_keywords.sort(key=lambda x: x[0].lower())
        elif sort_by == "length":
            filtered_keywords.sort(key=lambda x: len(x[0]))
        elif sort_by == "frequency":
            # Safety check before sorting
            filtered_keywords.sort(key=lambda x: self._metrics.get(x[0], {}).get('frequency', 0), reverse=True)
        else:  # score
            filtered_keywords.sort(key=lambda x: x[1], reverse=True)
        
        # Update tree with filtered and sorted data
        self._populate_keyword_tree_optimized(tree, filtered_keywords, self._metrics)
    
    def _suggest_category_name(self, keyword):
        """Suggest a category name based on keyword."""
        # Simple capitalization and cleanup
        suggestion = keyword.replace('_', ' ').title()
        
        # Check if it's an adult keyword and suggest appropriate category
        adult_keywords = ['adult', 'xxx', 'porn', 'sex', 'nsfw', 'mature', 'explicit']
        if any(adult_kw in keyword.lower() for adult_kw in adult_keywords):
            suggestion = f"Adult - {suggestion}"
        
        return suggestion
    
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
        
        preview_text.config(state='normal')
        preview_text.delete(1.0, tk.END)
        
        if not selected_items:
            preview_text.insert(tk.END, "No keywords selected.")
            preview_text.config(state='disabled')
            return
        
        # Get selected keywords
        selected_keywords = []
        for item in selected_items:
            keyword = tree.item(item, 'text')
            if keyword:
                selected_keywords.append(keyword)
        
        preview_text.insert(tk.END, f"Selected {len(selected_keywords)} keywords:\n\n")
        
        # Check if grouping is enabled (we need to access the checkbox from the dialog)
        # For now, show both grouped and individual previews
        
        # Show grouped preview
        if len(selected_keywords) > 1:
            category_groups = self._group_similar_keywords(selected_keywords)
            
            preview_text.insert(tk.END, "Grouped Categories:\n")
            total_bookmarks_grouped = 0
            
            for group_name, keywords in category_groups.items():
                bookmark_count = 0
                for keyword in keywords:
                    if keyword in self._metrics:
                        bookmark_count += self._metrics[keyword]['bookmark_count']
                
                total_bookmarks_grouped += bookmark_count
                keyword_list = ", ".join(keywords)
                preview_text.insert(tk.END, f"• {group_name}: {keyword_list} ({bookmark_count} bookmarks)\n")
            
            preview_text.insert(tk.END, f"\nTotal: {len(category_groups)} categories affecting {total_bookmarks_grouped} bookmarks\n\n")
        
        # Show individual preview
        preview_text.insert(tk.END, "Individual Categories:\n")
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
        
        for category, keywords in categories_preview.items():
            keyword_list = ", ".join([f"{kw} ({count})" for kw, count in keywords])
            preview_text.insert(tk.END, f"• {category}: {keyword_list}\n")
        
        preview_text.insert(tk.END, f"\nTotal: {len(categories_preview)} categories affecting {total_bookmarks} bookmarks")
        
        preview_text.config(state='disabled')
    
    def auto_categorize_bookmarks(self, group_similar=True, create_subcategories=False):
        """
        Automatically categorize bookmarks based on selected keywords.
        
        Args:
            group_similar (bool): Whether to group similar keywords into single categories
            create_subcategories (bool): Whether to create subcategories
        
        Returns:
            int: Number of bookmarks categorized, or None if operation was canceled
        """
        # Show keyword dialog
        dialog_result = self.show_keyword_dialog()
        if not dialog_result:
            return None
        
        # Extract keywords and settings from dialog result
        if isinstance(dialog_result, tuple) and len(dialog_result) == 3:
            selected_keywords, group_similar, create_subcategories = dialog_result
        elif isinstance(dialog_result, list):
            selected_keywords = dialog_result
            # Use default settings if not provided
        else:
            selected_keywords = dialog_result
            # Use default settings if not provided
        
        if not selected_keywords:
            return None
        
        # Create categories based on keywords
        link_controller = self.app.link_controller
        count = 0
        
        if group_similar:
            # Group similar keywords into combined categories
            category_groups = self._group_similar_keywords(selected_keywords)
            
            for group_name, keywords in category_groups.items():
                # Create category for the group
                category = link_controller._ensure_category_exists(group_name)
                
                # Find bookmarks matching any keyword in the group
                for bookmark in self.app.bookmarks:
                    if bookmark.category == "Uncategorized":
                        # Check if bookmark matches any keyword in this group
                        for keyword in keywords:
                            if self._keyword_matches_bookmark(keyword, bookmark):
                                link_controller.update_bookmark(bookmark, category=group_name)
                                count += 1
                                break  # Only categorize once per bookmark
        else:
            # Create individual categories for each keyword
            for keyword in selected_keywords:
                # Create category for each keyword
                category_name = self._suggest_category_name(keyword)
                category = link_controller._ensure_category_exists(category_name)
                
                # Find bookmarks matching keyword
                for bookmark in self.app.bookmarks:
                    if bookmark.category == "Uncategorized":
                        if self._keyword_matches_bookmark(keyword, bookmark):
                            link_controller.update_bookmark(bookmark, category=category_name)
                            count += 1
        
        # Clear cache after categorization
        self._keyword_cache.clear()
        
        messagebox.showinfo(
            "Auto-Categorization Complete",
            f"Categorized {count} bookmarks based on selected keywords."
        )
        return count
    
    def _group_similar_keywords(self, keywords):
        """
        Group similar keywords into combined categories.
        
        Args:
            keywords: List of keywords to group
            
        Returns:
            dict: Dictionary mapping group names to lists of keywords
        """
        groups = {}
        used_keywords = set()
        
        for keyword in keywords:
            if keyword in used_keywords:
                continue
                
            # Find similar keywords
            similar_keywords = [keyword]
            used_keywords.add(keyword)
            
            for other_keyword in keywords:
                if other_keyword != keyword and other_keyword not in used_keywords:
                    if self._keywords_are_similar(keyword, other_keyword):
                        similar_keywords.append(other_keyword)
                        used_keywords.add(other_keyword)
            
            # Create group name based on the most representative keyword
            if len(similar_keywords) == 1:
                group_name = self._suggest_category_name(keyword)
            else:
                # Use the shortest keyword as the group name, or combine them
                group_name = self._create_group_name(similar_keywords)
            
            groups[group_name] = similar_keywords
        
        return groups
    
    def _keywords_are_similar(self, keyword1, keyword2):
        """
        Check if two keywords are similar enough to be grouped.
        
        Args:
            keyword1: First keyword
            keyword2: Second keyword
            
        Returns:
            bool: True if keywords are similar
        """
        # Simple similarity checks
        k1_lower = keyword1.lower()
        k2_lower = keyword2.lower()
        
        # Check if one is contained in the other
        if k1_lower in k2_lower or k2_lower in k1_lower:
            return True
        
        # Check if they share significant words
        words1 = set(k1_lower.split())
        words2 = set(k2_lower.split())
        
        # If they share more than half of their words, consider them similar
        if len(words1.intersection(words2)) > 0:
            overlap_ratio = len(words1.intersection(words2)) / min(len(words1), len(words2))
            return overlap_ratio > 0.5
        
        return False
    
    def _create_group_name(self, keywords):
        """
        Create a group name from a list of similar keywords.
        
        Args:
            keywords: List of keywords to create a group name from
            
        Returns:
            str: Group name
        """
        # Find the shortest keyword as the base
        base_keyword = min(keywords, key=len)
        
        # Clean up the base keyword
        group_name = self._suggest_category_name(base_keyword)
        
        # If the base keyword is too short or generic, try to find a better one
        if len(base_keyword) < 4:
            longer_keywords = [k for k in keywords if len(k) >= 4]
            if longer_keywords:
                base_keyword = min(longer_keywords, key=len)
                group_name = self._suggest_category_name(base_keyword)
        
        return group_name
    
    def _keyword_matches_bookmark(self, keyword, bookmark):
        """
        Check if a keyword matches a bookmark using the same logic as metrics calculation.
        
        Args:
            keyword: The keyword to match
            bookmark: The bookmark to check
            
        Returns:
            bool: True if keyword matches bookmark
        """
        if ' ' in keyword:
            # Multi-word keyword - try exact match first, then word-by-word
            if keyword.lower() in bookmark.title.lower():
                return True
            
            # If no exact match, try matching all words in the phrase
            words = keyword.lower().split()
            return all(word in bookmark.title.lower() for word in words)
        else:
            # Single word keyword
            return keyword.lower() in bookmark.title.lower()
    
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