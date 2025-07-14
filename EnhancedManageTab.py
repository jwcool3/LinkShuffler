# Enhanced Manage Tab with Advanced Search, Sort, and Grouping
# This replaces your existing manage_tab.py with enhanced functionality

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import webbrowser
from typing import Dict, List
from enhanced_bookmark_features import (
    EnhancedBookmarkManager, SearchFilter, SortOrder, GroupBy,
    AdvancedSearchDialog, SortConfigDialog
)


class EnhancedManageTab:
    """Enhanced manage tab with advanced search, sort, and grouping features"""
    
    def __init__(self, app, parent):
        self.app = app
        self.parent = parent
        self.frame = parent
        
        # Initialize enhanced manager
        self.enhanced_manager = EnhancedBookmarkManager(app)
        
        # State variables
        self.current_bookmarks = []
        self.grouped_bookmarks = {}
        self.current_group_by = None
        self.current_search_filter = SearchFilter()
        self.current_sort = [("title", SortOrder.ASC)]
        
        # Pagination
        self.current_page = 0
        self.items_per_page = 25
        
        self.create_widgets()
        self.update_ui()
    
    def create_widgets(self):
        """Create the enhanced UI widgets"""
        
        # ======================
        # SEARCH AND FILTER BAR
        # ======================
        search_frame = ttk.LabelFrame(self.frame, text="Search & Filter")
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Quick search
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
        
        # ======================