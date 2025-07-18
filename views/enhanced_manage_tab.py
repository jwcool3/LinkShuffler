# Enhanced Manage Tab with Advanced Search, Sort, and Grouping
# This provides enhanced functionality for the manage tab with performance optimizations

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import webbrowser
import sys
import os
from typing import Dict, List
import time

# Add the parent directory to the path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.enhanced_bookmark_manager import (
    EnhancedBookmarkManager, SearchFilter, SortOrder, GroupBy,
    AdvancedSearchDialog, SortConfigDialog, LazyBookmarkLoader
)
from utils.validation import validate_and_normalize_url


class EnhancedManageTab:
    """Enhanced manage tab with advanced search, sort, and grouping features plus performance optimizations"""
    
    def __init__(self, app, parent):
        self.app = app
        self.parent = parent
        self.frame = parent
        
        # Get config settings
        self.config = getattr(app, 'config', None)
        
        # Initialize enhanced manager
        self.enhanced_manager = EnhancedBookmarkManager(app)
        
        # State variables
        self.current_bookmarks = []
        self.grouped_bookmarks = {}
        self.current_group_by = None
        self.current_search_filter = SearchFilter()
        self.current_sort = [("title", SortOrder.ASC)]
        
        # Performance and pagination from config
        self.current_page = 0
        self.items_per_page = self.config.default_page_size if self.config else 50
        self.total_pages = 0
        self.lazy_loader = None
        self.search_debounce_timer = None
        self.search_debounce_delay = self.config.search_debounce_delay if self.config else 300
        self.last_search_time = 0
        
        # Performance monitoring
        self.performance_stats = {}
        self.show_performance_monitor = self.config.show_performance_monitor if self.config else True
        
        self.create_widgets()
        self.update_ui()
        
        # Initialize lazy loading for large collections
        self._setup_lazy_loading()
    
    def _setup_lazy_loading(self):
        """Setup lazy loading if needed"""
        threshold = self.config.lazy_loading_threshold if self.config else 100
        if len(self.app.bookmarks) > threshold:
            self.lazy_loader = LazyBookmarkLoader(self.app.bookmarks, self.items_per_page)
            self.enhanced_manager.set_lazy_loading(True, threshold)
    
    def create_widgets(self):
        """Create the enhanced UI widgets with performance optimizations"""
        
        # ======================
        # PERFORMANCE MONITOR
        # ======================
        if self.show_performance_monitor:
            perf_frame = ttk.Frame(self.frame)
            perf_frame.pack(fill=tk.X, padx=10, pady=2)
            
            self.perf_label = ttk.Label(perf_frame, text="Performance: Ready", font=("Arial", 8))
            self.perf_label.pack(side=tk.LEFT)
            
            ttk.Button(perf_frame, text="Stats", command=self.show_performance_stats).pack(side=tk.RIGHT)
        
        # ======================
        # SEARCH AND FILTER BAR
        # ======================
        search_frame = ttk.LabelFrame(self.frame, text="Search & Filter")
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Quick search with configurable debouncing
        quick_search_frame = ttk.Frame(search_frame)
        quick_search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(quick_search_frame, text="Quick Search:").pack(side=tk.LEFT)
        self.quick_search_var = tk.StringVar()
        self.quick_search_entry = ttk.Entry(quick_search_frame, textvariable=self.quick_search_var, width=30)
        self.quick_search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.quick_search_entry.bind("<Return>", lambda e: self.quick_search())
        self.quick_search_entry.bind("<KeyRelease>", self.on_search_change)
        
        # Search buttons
        ttk.Button(quick_search_frame, text="Search", command=self.quick_search).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_search_frame, text="Advanced", command=self.advanced_search).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_search_frame, text="Clear", command=self.clear_search).pack(side=tk.LEFT, padx=2)
        
        # Quick filters
        filters_frame = ttk.Frame(search_frame)
        filters_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Category filter
        ttk.Label(filters_frame, text="Category:").pack(side=tk.LEFT)
        self.category_filter_var = tk.StringVar(value="All")
        self.category_filter = ttk.Combobox(
            filters_frame, textvariable=self.category_filter_var,
            state="readonly", width=15
        )
        self.category_filter.pack(side=tk.LEFT, padx=5)
        self.category_filter.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())
        
        # Rating filter
        ttk.Label(filters_frame, text="Min Rating:").pack(side=tk.LEFT, padx=(10, 0))
        self.rating_filter_var = tk.StringVar(value="All")
        self.rating_filter = ttk.Combobox(
            filters_frame, textvariable=self.rating_filter_var,
            values=["All", "1+", "2+", "3+", "4+", "5"], state="readonly", width=8
        )
        self.rating_filter.pack(side=tk.LEFT, padx=5)
        self.rating_filter.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())
        
        # Domain filter
        ttk.Label(filters_frame, text="Domain:").pack(side=tk.LEFT, padx=(10, 0))
        self.domain_filter_var = tk.StringVar(value="All")
        self.domain_filter = ttk.Combobox(
            filters_frame, textvariable=self.domain_filter_var,
            state="readonly", width=15
        )
        self.domain_filter.pack(side=tk.LEFT, padx=5)
        self.domain_filter.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())
        
        # ======================
        # SORTING AND GROUPING
        # ======================
        control_frame = ttk.LabelFrame(self.frame, text="Organization")
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Sort controls
        sort_frame = ttk.Frame(control_frame)
        sort_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        
        ttk.Label(sort_frame, text="Sort by:").pack(side=tk.LEFT)
        self.sort_field_var = tk.StringVar(value="title")
        self.sort_field = ttk.Combobox(
            sort_frame, textvariable=self.sort_field_var,
            values=["title", "url", "category", "rating", "date_added", "domain", "smart"],
            state="readonly", width=12
        )
        self.sort_field.pack(side=tk.LEFT, padx=5)
        self.sort_field.bind("<<ComboboxSelected>>", lambda e: self.apply_sort())
        
        self.sort_order_var = tk.StringVar(value="ascending")
        self.sort_order = ttk.Combobox(
            sort_frame, textvariable=self.sort_order_var,
            values=["ascending", "descending"], state="readonly", width=10
        )
        self.sort_order.pack(side=tk.LEFT, padx=5)
        self.sort_order.bind("<<ComboboxSelected>>", lambda e: self.apply_sort())
        
        ttk.Button(sort_frame, text="Multi-Sort", command=self.configure_multi_sort).pack(side=tk.LEFT, padx=5)
        
        # Group controls
        group_frame = ttk.Frame(control_frame)
        group_frame.pack(side=tk.RIGHT, padx=5, pady=5)
        
        ttk.Label(group_frame, text="Group by:").pack(side=tk.LEFT)
        self.group_by_var = tk.StringVar(value="None")
        self.group_by = ttk.Combobox(
            group_frame, textvariable=self.group_by_var,
            values=["None", "category", "domain", "rating", "date_added", "first_letter"],
            state="readonly", width=12
        )
        self.group_by.pack(side=tk.LEFT, padx=5)
        self.group_by.bind("<<ComboboxSelected>>", lambda e: self.apply_grouping())
        
        # ======================
        # PAGINATION CONTROLS
        # ======================
        pagination_frame = ttk.Frame(self.frame)
        pagination_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.page_label = ttk.Label(pagination_frame, text="Page 1 of 1")
        self.page_label.pack(side=tk.LEFT)
        
        ttk.Button(pagination_frame, text="◀◀", command=self.first_page).pack(side=tk.LEFT, padx=2)
        ttk.Button(pagination_frame, text="◀", command=self.prev_page).pack(side=tk.LEFT, padx=2)
        ttk.Button(pagination_frame, text="▶", command=self.next_page).pack(side=tk.LEFT, padx=2)
        ttk.Button(pagination_frame, text="▶▶", command=self.last_page).pack(side=tk.LEFT, padx=2)
        
        # Items per page
        ttk.Label(pagination_frame, text="Items per page:").pack(side=tk.RIGHT, padx=(10, 5))
        self.items_per_page_var = tk.StringVar(value=str(self.items_per_page))
        items_combo = ttk.Combobox(
            pagination_frame, textvariable=self.items_per_page_var,
            values=["25", "50", "100", "200"], state="readonly", width=8
        )
        items_combo.pack(side=tk.RIGHT, padx=5)
        items_combo.bind("<<ComboboxSelected>>", self.change_items_per_page)
        
        # ======================
        # BOOKMARKS DISPLAY
        # ======================
        display_frame = ttk.Frame(self.frame)
        display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create notebook for grouped/ungrouped views
        self.display_notebook = ttk.Notebook(display_frame)
        self.display_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Regular list view
        self.list_frame = ttk.Frame(self.display_notebook)
        self.display_notebook.add(self.list_frame, text="List View")
        
        # Create treeview for bookmarks
        tree_container = ttk.Frame(self.list_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        columns = ("title", "url", "category", "rating", "domain")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.tree.heading("title", text="Title", command=lambda: self.sort_by_column("title"))
        self.tree.heading("url", text="URL", command=lambda: self.sort_by_column("url"))
        self.tree.heading("category", text="Category", command=lambda: self.sort_by_column("category"))
        self.tree.heading("rating", text="Rating", command=lambda: self.sort_by_column("rating"))
        self.tree.heading("domain", text="Domain", command=lambda: self.sort_by_column("domain"))
        
        self.tree.column("title", width=250, minwidth=150)
        self.tree.column("url", width=300, minwidth=150)
        self.tree.column("category", width=120, minwidth=80)
        self.tree.column("rating", width=60, minwidth=50)
        self.tree.column("domain", width=150, minwidth=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Grouped view
        self.groups_frame = ttk.Frame(self.display_notebook)
        self.display_notebook.add(self.groups_frame, text="Grouped View")
        
        # Create scrollable frame for groups
        groups_canvas = tk.Canvas(self.groups_frame)
        groups_scrollbar = ttk.Scrollbar(self.groups_frame, orient=tk.VERTICAL, command=groups_canvas.yview)
        self.groups_content = ttk.Frame(groups_canvas)
        
        groups_canvas.configure(yscrollcommand=groups_scrollbar.set)
        groups_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        groups_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        groups_canvas.create_window((0, 0), window=self.groups_content, anchor="nw")
        self.groups_content.bind("<Configure>", lambda e: groups_canvas.configure(scrollregion=groups_canvas.bbox("all")))
        
        # Bind events
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Button-3>", self.show_context_menu)  # Right-click
        
        # ======================
        # ACTION BUTTONS
        # ======================
        action_frame = ttk.Frame(self.frame)
        action_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Left side - item actions
        item_actions = ttk.Frame(action_frame)
        item_actions.pack(side=tk.LEFT)
        
        ttk.Button(item_actions, text="Add Bookmark", command=self.add_bookmark).pack(side=tk.LEFT, padx=2)
        ttk.Button(item_actions, text="Edit", command=self.edit_bookmark).pack(side=tk.LEFT, padx=2)
        ttk.Button(item_actions, text="Delete", command=self.delete_bookmark).pack(side=tk.LEFT, padx=2)
        ttk.Button(item_actions, text="Open", command=self.open_bookmark).pack(side=tk.LEFT, padx=2)
        
        # Right side - bulk actions
        bulk_actions = ttk.Frame(action_frame)
        bulk_actions.pack(side=tk.RIGHT)
        
        ttk.Button(bulk_actions, text="Select All", command=self.select_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(bulk_actions, text="Bulk Edit", command=self.bulk_edit).pack(side=tk.LEFT, padx=2)
        ttk.Button(bulk_actions, text="Bulk Delete", command=self.bulk_delete).pack(side=tk.LEFT, padx=2)
        ttk.Button(bulk_actions, text="Export Selected", command=self.export_selected).pack(side=tk.LEFT, padx=2)
        
        # Status bar
        self.status_label = ttk.Label(self.frame, text="Ready")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=2)
        
        # Create context menu
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Open Link", command=self.open_bookmark)
        self.context_menu.add_command(label="Edit", command=self.edit_bookmark)
        self.context_menu.add_command(label="Delete", command=self.delete_bookmark)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Copy URL", command=self.copy_url)
        self.context_menu.add_command(label="Copy Title", command=self.copy_title)
    
    def update_ui(self):
        """Update the UI with current data and performance optimizations."""
        start_time = time.time()
        
        # Update category filter
        categories = sorted([c.name for c in self.app.categories])
        self.category_filter['values'] = ["All"] + categories
        
        # Update domain filter (use cached domain extraction)
        domains = list(set(self.enhanced_manager._get_domain(b) for b in self.app.bookmarks))
        domains = [d for d in domains if d]  # Remove empty domains
        self.domain_filter['values'] = ["All"] + sorted(domains)
        
        # Refresh search index
        self.enhanced_manager.refresh_indexes()
        
        # Apply current filters
        self.apply_filters()
        
        # Update performance stats
        self.last_search_time = time.time() - start_time
        self._update_performance_display()
    
    def quick_search(self):
        """Perform quick search with performance timing"""
        start_time = time.time()
        
        query = self.quick_search_var.get().strip()
        if query:
            search_filter = SearchFilter(query=query)
            self.current_bookmarks = self.enhanced_manager.advanced_search(search_filter)
        else:
            self.current_bookmarks = self.app.bookmarks.copy()
        
        self.current_page = 0  # Reset to first page
        self.refresh_display()
        
        self.last_search_time = time.time() - start_time
        self._update_performance_display()
    
    def on_search_change(self, event=None):
        """Handle search text change for real-time search with debouncing"""
        # Cancel previous timer
        if self.search_debounce_timer:
            self.frame.after_cancel(self.search_debounce_timer)
        
        # Set new timer for debounced search
        self.search_debounce_timer = self.frame.after(self.search_debounce_delay, self.quick_search)
    
    def advanced_search(self):
        """Show advanced search dialog with performance timing"""
        start_time = time.time()
        
        dialog = AdvancedSearchDialog(self.frame, self.app)
        self.frame.wait_window(dialog.dialog)
        
        if dialog.result:
            self.current_search_filter = dialog.result
            self.current_bookmarks = self.enhanced_manager.advanced_search(dialog.result)
            self.current_page = 0  # Reset to first page
            self.refresh_display()
        
        self.last_search_time = time.time() - start_time
        self._update_performance_display()
    
    def clear_search(self):
        """Clear all search filters"""
        self.quick_search_var.set("")
        self.category_filter_var.set("All")
        self.rating_filter_var.set("All")
        self.domain_filter_var.set("All")
        self.current_search_filter = SearchFilter()
        self.current_bookmarks = self.app.bookmarks.copy()
        self.current_page = 0
        self.refresh_display()
    
    def apply_filters(self):
        """Apply current filters with performance timing"""
        start_time = time.time()
        
        bookmarks = self.app.bookmarks.copy()
        
        # Apply category filter
        category = self.category_filter_var.get()
        if category != "All":
            bookmarks = [b for b in bookmarks if b.category == category]
        
        # Apply rating filter
        rating = self.rating_filter_var.get()
        if rating != "All":
            min_rating = int(rating[0])  # Extract number from "1+", "2+", etc.
            bookmarks = [b for b in bookmarks if b.rating and b.rating >= min_rating]
        
        # Apply domain filter (use cached domain extraction)
        domain = self.domain_filter_var.get()
        if domain != "All":
            bookmarks = [b for b in bookmarks if self.enhanced_manager._get_domain(b) == domain]
        
        self.current_bookmarks = bookmarks
        self.current_page = 0  # Reset to first page
        self.refresh_display()
        
        self.last_search_time = time.time() - start_time
        self._update_performance_display()
    
    def apply_sort(self):
        """Apply current sort settings with performance timing"""
        start_time = time.time()
        
        field = self.sort_field_var.get()
        order = SortOrder.ASC if self.sort_order_var.get() == "ascending" else SortOrder.DESC
        
        self.current_bookmarks = self.enhanced_manager.sort_bookmarks(
            self.current_bookmarks, field, order
        )
        self.refresh_display()
        
        self.last_search_time = time.time() - start_time
        self._update_performance_display()
    
    def configure_multi_sort(self):
        """Show multi-sort configuration dialog"""
        dialog = SortConfigDialog(self.frame)
        self.frame.wait_window(dialog.dialog)
        
        if dialog.result:
            start_time = time.time()
            
            self.current_sort = dialog.result
            self.current_bookmarks = self.enhanced_manager.multi_sort(
                self.current_bookmarks, dialog.result
            )
            self.refresh_display()
            
            self.last_search_time = time.time() - start_time
            self._update_performance_display()
    
    def apply_grouping(self):
        """Apply current grouping settings with performance timing"""
        start_time = time.time()
        
        group_by = self.group_by_var.get()
        
        if group_by == "None":
            self.current_group_by = None
            self.grouped_bookmarks = {}
            self.display_notebook.select(0)  # Switch to list view
        else:
            group_enum = getattr(GroupBy, group_by.upper())
            self.current_group_by = group_enum
            self.grouped_bookmarks = self.enhanced_manager.group_bookmarks(
                self.current_bookmarks, group_enum
            )
            self.display_notebook.select(1)  # Switch to grouped view
        
        self.refresh_display()
        
        self.last_search_time = time.time() - start_time
        self._update_performance_display()
    
    def refresh_display(self):
        """Refresh the display with current bookmarks using pagination"""
        if self.current_group_by is None:
            self.refresh_list_view()
        else:
            self.refresh_grouped_view()
        
        # Update pagination
        self._update_pagination_display()
        
        # Update status
        total = len(self.current_bookmarks)
        showing_start = self.current_page * self.items_per_page + 1
        showing_end = min(showing_start + self.items_per_page - 1, total)
        
        if total > 0:
            self.status_label.config(text=f"Showing {showing_start}-{showing_end} of {total} bookmarks")
        else:
            self.status_label.config(text="No bookmarks found")
    
    def refresh_list_view(self):
        """Refresh the list view with pagination"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Calculate pagination
        start_idx = self.current_page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.current_bookmarks))
        
        # Get bookmarks for current page
        if self.lazy_loader and len(self.current_bookmarks) > self.lazy_loader.lazy_loading_threshold:
            # Use lazy loading
            page_bookmarks = self.lazy_loader.get_page(self.current_page)
        else:
            # Use regular pagination
            page_bookmarks = self.current_bookmarks[start_idx:end_idx]
        
        # Add bookmarks to tree
        for bookmark in page_bookmarks:
            domain = self.enhanced_manager._get_domain(bookmark)
            rating_display = str(bookmark.rating) if bookmark.rating else ""
            
            self.tree.insert("", tk.END, values=(
                bookmark.title,
                bookmark.url,
                bookmark.category,
                rating_display,
                domain
            ))
    
    def refresh_grouped_view(self):
        """Refresh the grouped view with performance optimizations"""
        # Clear existing groups
        for widget in self.groups_content.winfo_children():
            widget.destroy()
        
        # Get limits from config
        max_groups = self.config.max_groups_display if self.config else 20
        max_bookmarks_per_group = self.config.max_bookmarks_per_group if self.config else 10
        
        groups_displayed = 0
        
        # Create group displays
        for group_name, bookmarks in self.grouped_bookmarks.items():
            if groups_displayed >= max_groups:
                # Add a label for remaining groups
                remaining_groups = len(self.grouped_bookmarks) - groups_displayed
                remaining_label = ttk.Label(
                    self.groups_content, 
                    text=f"... and {remaining_groups} more groups (use filters to narrow results)"
                )
                remaining_label.pack(fill=tk.X, padx=5, pady=5)
                break
            
            group_frame = ttk.LabelFrame(self.groups_content, text=f"{group_name} ({len(bookmarks)})")
            group_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Limit bookmarks displayed per group
            display_bookmarks = bookmarks[:max_bookmarks_per_group]
            
            # Create mini treeview for group
            group_tree = ttk.Treeview(group_frame, columns=("title", "url", "rating"), show="headings", height=min(5, len(display_bookmarks)))
            group_tree.heading("title", text="Title")
            group_tree.heading("url", text="URL")
            group_tree.heading("rating", text="Rating")
            
            group_tree.column("title", width=200)
            group_tree.column("url", width=300)
            group_tree.column("rating", width=60)
            
            for bookmark in display_bookmarks:
                rating_display = str(bookmark.rating) if bookmark.rating else ""
                group_tree.insert("", tk.END, values=(
                    bookmark.title,
                    bookmark.url,
                    rating_display
                ))
            
            group_tree.pack(fill=tk.X, padx=5, pady=5)
            
            # Add "show more" label if there are more bookmarks
            if len(bookmarks) > max_bookmarks_per_group:
                more_label = ttk.Label(
                    group_frame, 
                    text=f"... and {len(bookmarks) - max_bookmarks_per_group} more bookmarks",
                    font=("Arial", 8)
                )
                more_label.pack(padx=5, pady=2)
            
            groups_displayed += 1
    
    def sort_by_column(self, column):
        """Sort by clicking column header"""
        # Toggle sort order
        if self.sort_field_var.get() == column:
            current_order = self.sort_order_var.get()
            new_order = "descending" if current_order == "ascending" else "ascending"
            self.sort_order_var.set(new_order)
        else:
            self.sort_field_var.set(column)
            self.sort_order_var.set("ascending")
        
        self.apply_sort()
    
    def on_select(self, event):
        """Handle tree selection"""
        pass
    
    def on_double_click(self, event):
        """Handle double-click to edit"""
        self.edit_bookmark()
    
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def add_bookmark(self):
        """Add a new bookmark"""
        # Use the existing add bookmark dialog from the original manage tab
        if hasattr(self.app, 'main_window') and hasattr(self.app.main_window, 'manage_tab'):
            self.app.main_window.manage_tab.add_bookmark_dialog()
        else:
            # Create a simple add dialog
            self.show_bookmark_dialog()
    
    def edit_bookmark(self):
        """Edit selected bookmark"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a bookmark to edit.")
            return
        
        item = selection[0]
        values = self.tree.item(item, "values")
        url = values[1]
        
        # Find bookmark
        bookmark = None
        for b in self.app.bookmarks:
            if b.url == url:
                bookmark = b
                break
        
        if bookmark:
            self.show_bookmark_dialog(bookmark)
    
    def delete_bookmark(self):
        """Delete selected bookmark"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a bookmark to delete.")
            return
        
        # Check config for confirmation setting
        confirm_deletions = self.config.confirm_deletions if self.config else True
        
        if not confirm_deletions or messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected bookmark?"):
            item = selection[0]
            values = self.tree.item(item, "values")
            url = values[1]
            
            # Find and delete bookmark
            for bookmark in self.app.bookmarks[:]:
                if bookmark.url == url:
                    self.app.link_controller.delete_bookmark(bookmark)
                    break
            
            self.update_ui()
    
    def open_bookmark(self):
        """Open selected bookmark in browser"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a bookmark to open.")
            return
        
        item = selection[0]
        values = self.tree.item(item, "values")
        url = values[1]
        
        webbrowser.open(url)
    
    def select_all(self):
        """Select all bookmarks"""
        for item in self.tree.get_children():
            self.tree.selection_add(item)
    
    def bulk_edit(self):
        """Bulk edit selected bookmarks"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select bookmarks to edit.")
            return
        
        messagebox.showinfo("Not Implemented", "Bulk edit feature coming soon!")
    
    def bulk_delete(self):
        """Bulk delete selected bookmarks"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select bookmarks to delete.")
            return
        
        # Check config for confirmation setting
        confirm_deletions = self.config.confirm_deletions if self.config else True
        
        if not confirm_deletions or messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {len(selection)} bookmarks?"):
            for item in selection:
                values = self.tree.item(item, "values")
                url = values[1]
                
                # Find and delete bookmark
                for bookmark in self.app.bookmarks[:]:
                    if bookmark.url == url:
                        self.app.link_controller.delete_bookmark(bookmark)
                        break
            
            self.update_ui()
    
    def export_selected(self):
        """Export selected bookmarks"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select bookmarks to export.")
            return
        
        # Get selected bookmarks
        selected_bookmarks = []
        for item in selection:
            values = self.tree.item(item, "values")
            url = values[1]
            
            for bookmark in self.app.bookmarks:
                if bookmark.url == url:
                    selected_bookmarks.append(bookmark)
                    break
        
        # Export to CSV
        self.app.file_controller.export_to_csv(selected_bookmarks)
    
    def copy_url(self):
        """Copy URL to clipboard"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, "values")
            url = values[1]
            self.frame.clipboard_clear()
            self.frame.clipboard_append(url)
            self.status_label.config(text="URL copied to clipboard")
    
    def copy_title(self):
        """Copy title to clipboard"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, "values")
            title = values[0]
            self.frame.clipboard_clear()
            self.frame.clipboard_append(title)
            self.status_label.config(text="Title copied to clipboard")
    
    def show_bookmark_dialog(self, bookmark=None):
        """Show bookmark add/edit dialog"""
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Edit Bookmark" if bookmark else "Add Bookmark")
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.geometry("400x300")
        
        # Create form
        ttk.Label(dialog, text="Title:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        title_var = tk.StringVar(value=bookmark.title if bookmark else "")
        title_entry = ttk.Entry(dialog, textvariable=title_var, width=40)
        title_entry.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="URL:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        url_var = tk.StringVar(value=bookmark.url if bookmark else "")
        url_entry = ttk.Entry(dialog, textvariable=url_var, width=40)
        url_entry.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="Category:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        category_var = tk.StringVar(value=bookmark.category if bookmark else "Uncategorized")
        category_combo = ttk.Combobox(
            dialog, textvariable=category_var,
            values=sorted([c.name for c in self.app.categories]),
            width=38
        )
        category_combo.grid(row=2, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="Rating:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        rating_var = tk.StringVar(value=str(bookmark.rating) if bookmark and bookmark.rating else "")
        rating_combo = ttk.Combobox(
            dialog, textvariable=rating_var,
            values=["", "1", "2", "3", "4", "5"],
            width=38
        )
        rating_combo.grid(row=3, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # URL validation
        validation_label = ttk.Label(dialog, text="", foreground="red")
        validation_label.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        
        def validate_url_input(event=None):
            url = url_entry.get().strip()
            if url:
                is_valid, normalized_url, error_msg = validate_and_normalize_url(url)
                if not is_valid:
                    validation_label.config(text=error_msg, foreground="red")
                else:
                    validation_label.config(text="✓ Valid URL", foreground="green")
            else:
                validation_label.config(text="")
        
        url_entry.bind("<KeyRelease>", validate_url_input)
        
        def save_bookmark():
            title = title_var.get().strip()
            url = url_var.get().strip()
            category = category_var.get()
            rating_str = rating_var.get()
            
            if not title or not url:
                messagebox.showwarning("Missing Information", "Title and URL are required.")
                return
            
            is_valid, normalized_url, error_msg = validate_and_normalize_url(url)
            if not is_valid:
                messagebox.showerror("Invalid URL", f"URL validation failed: {error_msg}")
                return
            
            rating = int(rating_str) if rating_str else None
            
            if bookmark:
                # Update existing bookmark
                self.app.link_controller.update_bookmark(
                    bookmark, title=title, url=normalized_url, category=category, rating=rating
                )
            else:
                # Add new bookmark
                self.app.link_controller.create_bookmark(
                    url=normalized_url, title=title, category=category, rating=rating
                )
            
            dialog.destroy()
            self.update_ui()
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Save", command=save_bookmark).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        dialog.columnconfigure(1, weight=1)
        title_entry.focus_set() 

    # ======================
    # PERFORMANCE METHODS
    # ======================
    
    def show_performance_stats(self):
        """Show performance statistics dialog"""
        stats = self.enhanced_manager.get_performance_stats()
        
        dialog = tk.Toplevel(self.frame)
        dialog.title("Performance Statistics")
        dialog.geometry("400x300")
        dialog.transient(self.frame)
        dialog.grab_set()
        
        text_widget = tk.Text(dialog, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        stats_text = f"""Performance Statistics:

Total Bookmarks: {stats['total_bookmarks']}
Search Index Built: {stats['search_index_built']}
Using Lazy Loading: {stats['using_lazy_loading']}
Using Database: {stats['using_database']}
Search History Size: {stats['search_history_size']}
Background Tasks: {stats['background_tasks']}

Current Page: {self.current_page + 1} of {self.total_pages}
Items Per Page: {self.items_per_page}
Last Search Time: {self.last_search_time:.3f}s

Memory Usage:
- Current Bookmarks: {len(self.current_bookmarks)} items
- Grouped Bookmarks: {len(self.grouped_bookmarks)} groups
"""
        
        text_widget.insert(tk.END, stats_text)
        text_widget.config(state=tk.DISABLED)
        
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)
    
    def _update_performance_display(self):
        """Update performance display"""
        stats = self.enhanced_manager.get_performance_stats()
        perf_text = f"Bookmarks: {stats['total_bookmarks']} | "
        perf_text += f"Indexed: {'Yes' if stats['search_index_built'] else 'No'} | "
        perf_text += f"Page: {self.current_page + 1}/{self.total_pages}"
        
        self.perf_label.config(text=perf_text)
    
    # ======================
    # PAGINATION METHODS
    # ======================
    
    def change_items_per_page(self, event=None):
        """Change items per page"""
        try:
            new_items_per_page = int(self.items_per_page_var.get())
            self.items_per_page = new_items_per_page
            self.current_page = 0
            self._setup_lazy_loading()
            self.refresh_display()
        except ValueError:
            pass
    
    def first_page(self):
        """Go to first page"""
        self.current_page = 0
        self.refresh_display()
    
    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.refresh_display()
    
    def next_page(self):
        """Go to next page"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.refresh_display()
    
    def last_page(self):
        """Go to last page"""
        self.current_page = max(0, self.total_pages - 1)
        self.refresh_display()
    
    def _update_pagination_display(self):
        """Update pagination display"""
        self.total_pages = max(1, (len(self.current_bookmarks) + self.items_per_page - 1) // self.items_per_page)
        self.page_label.config(text=f"Page {self.current_page + 1} of {self.total_pages}")
        self._update_performance_display() 