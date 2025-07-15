import re
import tkinter as tk
from tkinter import messagebox, Toplevel, ttk
from collections import defaultdict, Counter
from urllib.parse import urlparse
import threading
import time

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class EnhancedKeywordController:
    """
    Enhanced controller for intelligent keyword detection and auto-categorization.
    """
    def __init__(self, app):
        self.app = app
        self.adult_platforms = {
            'pornhub.com': 'PornHub',
            'xvideos.com': 'XVideos', 
            'xhamster.com': 'XHamster',
            'redtube.com': 'RedTube',
            'youporn.com': 'YouPorn',
            'tube8.com': 'Tube8',
            'spankbang.com': 'SpankBang',
            'eporner.com': 'ePortner',
            'xnxx.com': 'XNXX',
            'tnaflix.com': 'TNAFlix',
            'porndig.com': 'PornDig',
            'txxx.com': 'TXXX'
        }
        
        # Enhanced keyword patterns for adult content
        self.adult_keywords = {
            'performers': ['milf', 'teen', 'mature', 'latina', 'asian', 'blonde', 'brunette', 'redhead'],
            'categories': ['anal', 'oral', 'hardcore', 'softcore', 'amateur', 'professional', 'pov', 'threesome'],
            'content_type': ['video', 'gallery', 'live', 'cam', 'story', 'audio'],
            'quality': ['hd', '4k', '1080p', '720p', 'uhd', 'vr'],
            'duration': ['short', 'long', 'full', 'clip', 'movie', 'scene']
        }
        
        # General website categories
        self.general_categories = {
            'social': ['facebook', 'twitter', 'instagram', 'linkedin', 'reddit', 'tiktok'],
            'shopping': ['amazon', 'ebay', 'shop', 'store', 'buy', 'sale'],
            'news': ['news', 'article', 'blog', 'press', 'media', 'journal'],
            'tech': ['github', 'stackoverflow', 'tech', 'code', 'programming', 'software'],
            'entertainment': ['youtube', 'netflix', 'movie', 'music', 'game', 'stream'],
            'education': ['course', 'tutorial', 'learn', 'education', 'university', 'school'],
            'work': ['work', 'job', 'career', 'office', 'business', 'professional']
        }
    
    def analyze_bookmarks_intelligent(self):
        """
        Intelligent analysis of bookmarks with automatic categorization suggestions.
        """
        if not self.app.bookmarks:
            messagebox.showwarning("No Bookmarks", "No bookmarks loaded to analyze.")
            return
        
        # Show progress dialog
        progress_dialog = self._create_progress_dialog()
        
        # Run analysis in background thread
        def analyze_thread():
            try:
                analysis_results = self._perform_intelligent_analysis()
                
                # Close progress dialog
                progress_dialog.destroy()
                
                # Show results dialog
                if analysis_results:
                    self._show_intelligent_categorization_dialog(analysis_results)
                else:
                    messagebox.showinfo("Analysis Complete", "No categorization suggestions found.")
                    
            except Exception as e:
                progress_dialog.destroy()
                messagebox.showerror("Error", f"Analysis failed: {str(e)}")
        
        # Start analysis thread
        thread = threading.Thread(target=analyze_thread)
        thread.daemon = True
        thread.start()
    
    def _create_progress_dialog(self):
        """Create a progress dialog for analysis."""
        dialog = Toplevel(self.app.root)
        dialog.title("Analyzing Bookmarks...")
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (150 // 2)
        dialog.geometry(f"400x150+{x}+{y}")
        
        # Progress label
        tk.Label(dialog, text="Analyzing bookmarks and detecting patterns...", 
                font=('Arial', 10)).pack(pady=20)
        
        # Progress bar
        progress = ttk.Progressbar(dialog, mode='indeterminate')
        progress.pack(pady=10, padx=20, fill='x')
        progress.start()
        
        # Status label
        status_label = tk.Label(dialog, text="Processing...", fg='gray')
        status_label.pack(pady=5)
        
        return dialog
    
    def _perform_intelligent_analysis(self):
        """
        Perform intelligent analysis of bookmarks.
        
        Returns:
            dict: Analysis results with categorization suggestions
        """
        results = {
            'platform_categories': defaultdict(list),
            'keyword_categories': defaultdict(list),
            'cluster_categories': defaultdict(list),
            'suggested_categories': set(),
            'uncategorized_bookmarks': []
        }
        
        # Step 1: Platform-based categorization
        for bookmark in self.app.bookmarks:
            if bookmark.category == "Uncategorized":
                platform_category = self._detect_platform_category(bookmark)
                if platform_category:
                    results['platform_categories'][platform_category].append(bookmark)
                    results['suggested_categories'].add(platform_category)
                else:
                    results['uncategorized_bookmarks'].append(bookmark)
        
        # Step 2: Keyword-based categorization
        for bookmark in results['uncategorized_bookmarks'][:]:
            keyword_category = self._detect_keyword_category(bookmark)
            if keyword_category:
                results['keyword_categories'][keyword_category].append(bookmark)
                results['suggested_categories'].add(keyword_category)
                results['uncategorized_bookmarks'].remove(bookmark)
        
        # Step 3: Clustering-based categorization (if sklearn available)
        if SKLEARN_AVAILABLE and results['uncategorized_bookmarks']:
            cluster_results = self._perform_clustering_analysis(results['uncategorized_bookmarks'])
            if cluster_results:
                results['cluster_categories'].update(cluster_results)
                # Remove clustered bookmarks from uncategorized
                for cluster_bookmarks in cluster_results.values():
                    for bookmark in cluster_bookmarks:
                        if bookmark in results['uncategorized_bookmarks']:
                            results['uncategorized_bookmarks'].remove(bookmark)
        
        return results
    
    def _detect_platform_category(self, bookmark):
        """Detect category based on platform/domain."""
        if not bookmark.url:
            return None
        
        try:
            domain = urlparse(bookmark.url).netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Check for adult platforms
            for platform_domain, platform_name in self.adult_platforms.items():
                if platform_domain in domain:
                    return f"Adult - {platform_name}"
            
            # Check for general platforms
            for category, keywords in self.general_categories.items():
                for keyword in keywords:
                    if keyword in domain:
                        return category.title()
            
            return None
            
        except Exception:
            return None
    
    def _detect_keyword_category(self, bookmark):
        """Detect category based on title keywords."""
        if not bookmark.title:
            return None
        
        title_lower = bookmark.title.lower()
        
        # Check adult keywords
        for category, keywords in self.adult_keywords.items():
            for keyword in keywords:
                if keyword in title_lower:
                    return f"Adult - {category.title()}"
        
        # Check general keywords
        for category, keywords in self.general_categories.items():
            for keyword in keywords:
                if keyword in title_lower:
                    return category.title()
        
        return None
    
    def _perform_clustering_analysis(self, bookmarks):
        """Perform clustering analysis on uncategorized bookmarks."""
        if len(bookmarks) < 3:  # Need at least 3 bookmarks for clustering
            return {}
        
        try:
            # Prepare text data
            texts = []
            for bookmark in bookmarks:
                text = f"{bookmark.title} {bookmark.url}"
                texts.append(text)
            
            # Vectorize
            vectorizer = TfidfVectorizer(
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.8,
                max_features=100
            )
            
            X = vectorizer.fit_transform(texts)
            
            # Determine optimal number of clusters
            n_clusters = min(5, len(bookmarks) // 2)
            if n_clusters < 2:
                return {}
            
            # Perform clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(X)
            
            # Group bookmarks by cluster
            cluster_results = defaultdict(list)
            for i, cluster_id in enumerate(clusters):
                cluster_results[f"Cluster {cluster_id + 1}"].append(bookmarks[i])
            
            # Filter out single-item clusters
            cluster_results = {k: v for k, v in cluster_results.items() if len(v) > 1}
            
            return cluster_results
            
        except Exception as e:
            print(f"Clustering analysis failed: {e}")
            return {}
    
    def _show_intelligent_categorization_dialog(self, results):
        """Show enhanced categorization dialog with preview and options."""
        dialog = Toplevel(self.app.root)
        dialog.title("🧠 Intelligent Categorization Results")
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.geometry("1000x700")
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500)
        y = (dialog.winfo_screenheight() // 2) - (350)
        dialog.geometry(f"1000x700+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title and summary
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(title_frame, text="Intelligent Categorization Results", 
                 font=('Arial', 16, 'bold')).pack(anchor='w')
        
        # Summary stats
        total_categories = len(results['platform_categories']) + len(results['keyword_categories']) + len(results['cluster_categories'])
        total_bookmarks = sum(len(bookmarks) for bookmarks in results['platform_categories'].values())
        total_bookmarks += sum(len(bookmarks) for bookmarks in results['keyword_categories'].values())
        total_bookmarks += sum(len(bookmarks) for bookmarks in results['cluster_categories'].values())
        
        summary_text = f"Found {total_categories} suggested categories for {total_bookmarks} bookmarks"
        if results['uncategorized_bookmarks']:
            summary_text += f" ({len(results['uncategorized_bookmarks'])} remain uncategorized)"
        
        ttk.Label(title_frame, text=summary_text, 
                 font=('Arial', 11)).pack(anchor='w')
        
        # Control frame
        control_frame = ttk.LabelFrame(main_frame, text="View Options")
        control_frame.pack(fill='x', pady=(0, 10))
        
        control_row = ttk.Frame(control_frame)
        control_row.pack(fill='x', padx=5, pady=5)
        
        # Sort options
        ttk.Label(control_row, text="Sort by:").pack(side='left', padx=(0, 5))
        sort_var = tk.StringVar(value="bookmark_count")
        sort_combo = ttk.Combobox(control_row, textvariable=sort_var, width=15, state="readonly",
                                 values=["bookmark_count", "alphabetical", "category_type"])
        sort_combo.pack(side='left', padx=(0, 15))
        
        # Filter options
        ttk.Label(control_row, text="Filter:").pack(side='left', padx=(0, 5))
        filter_var = tk.StringVar()
        filter_entry = ttk.Entry(control_row, textvariable=filter_var, width=20)
        filter_entry.pack(side='left', padx=(0, 15))
        
        # Selection options
        ttk.Button(control_row, text="Select All", 
                  command=lambda: self._select_all_categories(notebook)).pack(side='left', padx=(0, 5))
        ttk.Button(control_row, text="Select None", 
                  command=lambda: self._select_none_categories(notebook)).pack(side='left', padx=(0, 5))
        ttk.Button(control_row, text="Select High Impact", 
                  command=lambda: self._select_high_impact_categories(notebook)).pack(side='left', padx=(0, 5))
        
        # Create notebook for different result types
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True, pady=(0, 10))
        
        # Store trees for later access
        self.category_trees = {}
        
        # Platform-based results
        if results['platform_categories']:
            platform_frame = ttk.Frame(notebook)
            platform_tab_text = f"🌐 Platform-based ({len(results['platform_categories'])} categories)"
            notebook.add(platform_frame, text=platform_tab_text)
            self.category_trees['platform'] = self._create_enhanced_category_tree(
                platform_frame, results['platform_categories'], "Platform Detection")
        
        # Keyword-based results
        if results['keyword_categories']:
            keyword_frame = ttk.Frame(notebook)
            keyword_tab_text = f"🔍 Keyword-based ({len(results['keyword_categories'])} categories)"
            notebook.add(keyword_frame, text=keyword_tab_text)
            self.category_trees['keyword'] = self._create_enhanced_category_tree(
                keyword_frame, results['keyword_categories'], "Keyword Analysis")
        
        # Cluster-based results
        if results['cluster_categories']:
            cluster_frame = ttk.Frame(notebook)
            cluster_tab_text = f"🤖 AI Clusters ({len(results['cluster_categories'])} groups)"
            notebook.add(cluster_frame, text=cluster_tab_text)
            self.category_trees['cluster'] = self._create_enhanced_category_tree(
                cluster_frame, results['cluster_categories'], "AI Clustering")
        
        # Preview frame
        preview_frame = ttk.LabelFrame(main_frame, text="📋 Selection Preview")
        preview_frame.pack(fill='x', pady=(0, 10))
        
        preview_text = tk.Text(preview_frame, height=6, wrap='word')
        preview_scrollbar = ttk.Scrollbar(preview_frame, orient='vertical', command=preview_text.yview)
        preview_text.configure(yscrollcommand=preview_scrollbar.set)
        
        preview_text.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        preview_scrollbar.pack(side='right', fill='y', pady=5)
        
        # Bind events
        def on_sort_change(*args):
            self._sort_all_category_trees(sort_var.get())
        
        def on_filter_change(*args):
            self._filter_all_category_trees(filter_var.get())
        
        def on_tree_selection_change(*args):
            self._update_categorization_preview(preview_text)
        
        sort_var.trace('w', on_sort_change)
        filter_var.trace('w', on_filter_change)
        
        # Bind selection events to all trees
        for tree in self.category_trees.values():
            tree.bind('<<TreeviewSelect>>', on_tree_selection_change)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Apply selected button
        def apply_selected():
            self._apply_selected_categorization_results(results, dialog)
        
        def apply_all():
            self._apply_all_categorization_results(results, dialog)
        
        def preview_changes():
            self._preview_categorization_changes(results)
        
        # Buttons with icons
        ttk.Button(button_frame, text="🔍 Preview Changes", 
                  command=preview_changes).pack(side='left', padx=(0, 5))
        ttk.Button(button_frame, text="✅ Apply Selected", 
                  command=apply_selected).pack(side='left', padx=(0, 5))
        ttk.Button(button_frame, text="⚡ Apply All", 
                  command=apply_all).pack(side='left', padx=(0, 5))
        ttk.Button(button_frame, text="❌ Cancel", 
                  command=dialog.destroy).pack(side='right')
        
        # Store results in dialog for access by button callbacks
        dialog.results = results
        
        # Update initial preview
        self._update_categorization_preview(preview_text)
    
    def _create_enhanced_category_tree(self, parent, categories, analysis_type):
        """Create an enhanced tree view for category results."""
        # Header frame
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(header_frame, text=f"{analysis_type} Results", 
                 font=('Arial', 12, 'bold')).pack(anchor='w')
        ttk.Label(header_frame, text=f"Categories found through {analysis_type.lower()}", 
                 font=('Arial', 10), foreground='gray').pack(anchor='w')
        
        # Create treeview with enhanced columns
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ('count', 'confidence', 'impact')
        tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings')
        tree.heading('#0', text='Category')
        tree.heading('count', text='Bookmarks')
        tree.heading('confidence', text='Confidence')
        tree.heading('impact', text='Impact')
        
        # Configure column widths
        tree.column('#0', width=250)
        tree.column('count', width=80)
        tree.column('confidence', width=80)
        tree.column('impact', width=80)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Populate tree
        for category, bookmarks in categories.items():
            confidence = self._calculate_confidence(category, bookmarks, analysis_type)
            impact = self._calculate_impact(bookmarks)
            
            category_id = tree.insert('', 'end', text=category, values=(
                len(bookmarks), f"{confidence:.1f}%", impact
            ))
            
            # Add bookmark children (limited to first 10 for performance)
            for i, bookmark in enumerate(bookmarks[:10]):
                display_title = bookmark.title[:50] + "..." if len(bookmark.title) > 50 else bookmark.title
                tree.insert(category_id, 'end', text=display_title, values=('', '', ''))
            
            if len(bookmarks) > 10:
                tree.insert(category_id, 'end', text=f"... and {len(bookmarks) - 10} more", 
                           values=('', '', ''))
        
        # Expand all categories initially
        for item in tree.get_children():
            tree.item(item, open=True)
        
        return tree
    
    def _calculate_confidence(self, category, bookmarks, analysis_type):
        """Calculate confidence score for a category."""
        if analysis_type == "Platform Detection":
            return 95.0  # High confidence for platform-based
        elif analysis_type == "Keyword Analysis":
            return 80.0  # Good confidence for keyword-based
        else:  # AI Clustering
            return 70.0  # Moderate confidence for clustering
    
    def _calculate_impact(self, bookmarks):
        """Calculate impact level for a category."""
        count = len(bookmarks)
        if count >= 10:
            return "High"
        elif count >= 5:
            return "Medium"
        else:
            return "Low"
    
    def _select_all_categories(self, notebook):
        """Select all categories in all tabs."""
        for tree in self.category_trees.values():
            tree.selection_set(tree.get_children())
    
    def _select_none_categories(self, notebook):
        """Deselect all categories in all tabs."""
        for tree in self.category_trees.values():
            tree.selection_remove(tree.get_children())
    
    def _select_high_impact_categories(self, notebook):
        """Select high impact categories."""
        for tree in self.category_trees.values():
            for item in tree.get_children():
                values = tree.item(item, 'values')
                if values and len(values) > 2 and values[2] == "High":
                    tree.selection_add(item)
    
    def _sort_all_category_trees(self, sort_by):
        """Sort all category trees by the specified criteria."""
        # This would require rebuilding the trees with sorted data
        # For now, just a placeholder
        pass
    
    def _filter_all_category_trees(self, filter_text):
        """Filter all category trees based on text."""
        # This would require filtering the tree items
        # For now, just a placeholder
        pass
    
    def _update_categorization_preview(self, preview_text):
        """Update the preview text with selected categories."""
        preview_text.delete(1.0, tk.END)
        
        selected_categories = {}
        total_bookmarks = 0
        
        for tree_type, tree in self.category_trees.items():
            for item in tree.selection():
                category_name = tree.item(item, 'text')
                values = tree.item(item, 'values')
                
                if values and values[0].isdigit():  # It's a category, not a bookmark
                    bookmark_count = int(values[0])
                    selected_categories[category_name] = {
                        'count': bookmark_count,
                        'type': tree_type,
                        'confidence': values[1] if len(values) > 1 else 'N/A',
                        'impact': values[2] if len(values) > 2 else 'N/A'
                    }
                    total_bookmarks += bookmark_count
        
        if not selected_categories:
            preview_text.insert(tk.END, "No categories selected.\n\nSelect categories from the tabs above to see a preview of the changes.")
            return
        
        preview_text.insert(tk.END, f"📊 CATEGORIZATION PREVIEW\n")
        preview_text.insert(tk.END, f"{'='*50}\n\n")
        preview_text.insert(tk.END, f"Selected {len(selected_categories)} categories affecting {total_bookmarks} bookmarks:\n\n")
        
        # Group by type
        by_type = {}
        for cat_name, cat_info in selected_categories.items():
            cat_type = cat_info['type']
            if cat_type not in by_type:
                by_type[cat_type] = []
            by_type[cat_type].append((cat_name, cat_info))
        
        for cat_type, categories in by_type.items():
            type_names = {'platform': '🌐 Platform-based', 'keyword': '🔍 Keyword-based', 'cluster': '🤖 AI Clusters'}
            preview_text.insert(tk.END, f"{type_names.get(cat_type, cat_type)}:\n")
            
            for cat_name, cat_info in categories:
                preview_text.insert(tk.END, f"  • {cat_name}: {cat_info['count']} bookmarks "
                                           f"(Confidence: {cat_info['confidence']}, Impact: {cat_info['impact']})\n")
            preview_text.insert(tk.END, "\n")
    
    def _apply_selected_categorization_results(self, results, dialog):
        """Apply only selected categorization results."""
        count = 0
        
        for tree_type, tree in self.category_trees.items():
            for item in tree.selection():
                category_name = tree.item(item, 'text')
                values = tree.item(item, 'values')
                
                if values and values[0].isdigit():  # It's a category, not a bookmark
                    # Find the bookmarks for this category
                    bookmarks = None
                    if tree_type == 'platform':
                        bookmarks = results['platform_categories'].get(category_name, [])
                    elif tree_type == 'keyword':
                        bookmarks = results['keyword_categories'].get(category_name, [])
                    elif tree_type == 'cluster':
                        bookmarks = results['cluster_categories'].get(category_name, [])
                    
                    if bookmarks:
                        self._create_category_and_assign(category_name, bookmarks)
                        count += len(bookmarks)
        
        dialog.destroy()
        
        if count > 0:
            messagebox.showinfo(
                "Categorization Complete",
                f"Successfully categorized {count} bookmarks."
            )
            
            # Refresh the UI
            if hasattr(self.app, 'main_window'):
                self.app.main_window.refresh_all_tabs()
        else:
            messagebox.showinfo("No Changes", "No categories were selected for application.")
    
    def _preview_categorization_changes(self, results):
        """Show a detailed preview of what changes will be made."""
        # This could open another dialog showing exactly which bookmarks will be moved
        messagebox.showinfo("Preview", "Detailed preview feature coming soon!")
    
    def _apply_all_categorization_results(self, results, dialog):
        """Apply all categorization results."""
        count = 0
        
        # Apply platform-based categorization
        for category, bookmarks in results['platform_categories'].items():
            self._create_category_and_assign(category, bookmarks)
            count += len(bookmarks)
        
        # Apply keyword-based categorization
        for category, bookmarks in results['keyword_categories'].items():
            self._create_category_and_assign(category, bookmarks)
            count += len(bookmarks)
        
        # Apply cluster-based categorization
        for category, bookmarks in results['cluster_categories'].items():
            self._create_category_and_assign(category, bookmarks)
            count += len(bookmarks)
        
        dialog.destroy()
        
        messagebox.showinfo(
            "Categorization Complete",
            f"Successfully categorized {count} bookmarks into {len(results['suggested_categories'])} categories."
        )
        
        # Refresh the UI
        if hasattr(self.app, 'main_window'):
            self.app.main_window.refresh_all_tabs()
    
    def _create_category_and_assign(self, category_name, bookmarks):
        """Create category if it doesn't exist and assign bookmarks to it."""
        # Ensure category exists
        link_controller = self.app.link_controller
        category = link_controller._ensure_category_exists(category_name)
        
        # Assign bookmarks to category
        for bookmark in bookmarks:
            link_controller.update_bookmark(bookmark, category=category_name)
    
    def quick_auto_categorize(self):
        """Quick automatic categorization without dialog."""
        if not self.app.bookmarks:
            messagebox.showwarning("No Bookmarks", "No bookmarks loaded to categorize.")
            return
        
        count = 0
        uncategorized = [b for b in self.app.bookmarks if b.category == "Uncategorized"]
        
        for bookmark in uncategorized:
            # Try platform-based categorization first
            category = self._detect_platform_category(bookmark)
            if not category:
                # Try keyword-based categorization
                category = self._detect_keyword_category(bookmark)
            
            if category:
                self._create_category_and_assign(category, [bookmark])
                count += 1
        
        if count > 0:
            messagebox.showinfo(
                "Quick Categorization Complete",
                f"Automatically categorized {count} bookmarks."
            )
            
            # Refresh the UI
            if hasattr(self.app, 'main_window'):
                self.app.main_window.refresh_all_tabs()
        else:
            messagebox.showinfo(
                "No Categorization",
                "No bookmarks could be automatically categorized."
            ) 