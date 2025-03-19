import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import webbrowser

class ManageTab:
    """
    Manage tab view for the BookmarkShuffler application.
    """
    def __init__(self, app, parent):
        """
        Initialize the manage tab.
        
        Args:
            app: The main application instance
            parent: The parent widget (frame)
        """
        self.app = app
        self.parent = parent
        
        # Use the provided frame directly
        self.frame = parent
        
        # Create top controls frame
        controls_frame = ttk.Frame(self.frame)
        controls_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Search frame
        search_frame = ttk.LabelFrame(controls_frame, text="Search")
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Search entry
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        search_entry.bind("<Return>", lambda e: self.filter_bookmarks())
        
        # Search button
        search_button = ttk.Button(search_frame, text="Search", command=self.filter_bookmarks)
        search_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Reset button
        reset_button = ttk.Button(search_frame, text="Reset", command=self.reset_filters)
        reset_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Filter frame
        filter_frame = ttk.LabelFrame(controls_frame, text="Filter")
        filter_frame.pack(side=tk.LEFT, fill=tk.X, padx=5)
        
        # Category filter
        ttk.Label(filter_frame, text="Category:").pack(side=tk.LEFT, padx=5, pady=5)
        
        self.category_var = tk.StringVar(value="All")
        self.category_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.category_var,
            state="readonly",
            width=15
        )
        self.category_combo.pack(side=tk.LEFT, padx=5, pady=5)
        self.category_combo.bind("<<ComboboxSelected>>", lambda e: self.filter_bookmarks())
        
        # Rating filter
        ttk.Label(filter_frame, text="Rating:").pack(side=tk.LEFT, padx=5, pady=5)
        
        self.rating_var = tk.StringVar(value="All")
        self.rating_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.rating_var,
            values=["All", "1", "2", "3", "4", "5"],
            state="readonly",
            width=5
        )
        self.rating_combo.pack(side=tk.LEFT, padx=5, pady=5)
        self.rating_combo.bind("<<ComboboxSelected>>", lambda e: self.filter_bookmarks())
        
        # Add button frame
        add_frame = ttk.Frame(controls_frame)
        add_frame.pack(side=tk.LEFT, fill=tk.X, padx=5)
        
        # Add bookmark button
        add_button = ttk.Button(add_frame, text="Add Bookmark", command=self.add_bookmark_dialog)
        add_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Create treeview for bookmarks
        tree_frame = ttk.Frame(self.frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Column definitions
        columns = ("title", "url", "category", "rating")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        # Define headings
        self.tree.heading("title", text="Title", command=lambda: self.sort_column("title", False))
        self.tree.heading("url", text="URL", command=lambda: self.sort_column("url", False))
        self.tree.heading("category", text="Category", command=lambda: self.sort_column("category", False))
        self.tree.heading("rating", text="Rating", command=lambda: self.sort_column("rating", False))
        
        # Set column widths
        self.tree.column("title", width=300, minwidth=150)
        self.tree.column("url", width=300, minwidth=150)
        self.tree.column("category", width=150, minwidth=100)
        self.tree.column("rating", width=50, minwidth=50)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind events
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<Double-1>", self.on_double_click)
        
        # Action buttons frame
        action_frame = ttk.Frame(self.frame)
        action_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Edit button
        edit_button = ttk.Button(action_frame, text="Edit", command=self.edit_bookmark)
        edit_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Delete button
        delete_button = ttk.Button(action_frame, text="Delete", command=self.delete_bookmark)
        delete_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Open button
        open_button = ttk.Button(action_frame, text="Open in Browser", command=self.open_selected)
        open_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Bulk action frame
        bulk_frame = ttk.LabelFrame(self.frame, text="Bulk Actions")
        bulk_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Bulk categorize
        bulk_cat_button = ttk.Button(bulk_frame, text="Categorize Selected", command=self.bulk_categorize)
        bulk_cat_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Bulk delete
        bulk_del_button = ttk.Button(bulk_frame, text="Delete Selected", command=self.bulk_delete)
        bulk_del_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Pagination frame
        pagination_frame = ttk.Frame(self.frame)
        pagination_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Page info label
        self.page_info_var = tk.StringVar(value="Page 1 of 1")
        page_info_label = ttk.Label(pagination_frame, textvariable=self.page_info_var)
        page_info_label.pack(side=tk.LEFT, padx=5)
        
        # Previous page button
        prev_button = ttk.Button(pagination_frame, text="Previous", command=lambda: self.change_page(-1))
        prev_button.pack(side=tk.LEFT, padx=5)
        
        # Next page button
        next_button = ttk.Button(pagination_frame, text="Next", command=lambda: self.change_page(1))
        next_button.pack(side=tk.LEFT, padx=5)
        
        # Page size
        ttk.Label(pagination_frame, text="Items per page:").pack(side=tk.LEFT, padx=5)
        
        self.page_size_var = tk.IntVar(value=25)
        page_size_spin = ttk.Spinbox(
            pagination_frame,
            from_=10,
            to=100,
            increment=5,
            textvariable=self.page_size_var,
            width=5,
            command=self.update_page_size
        )
        page_size_spin.pack(side=tk.LEFT, padx=5)
        
        # Status variables
        self.current_page = 0
        self.filtered_bookmarks = []
        
        # Create a status label for this tab
        self.status_label = ttk.Label(self.frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Update UI (delay initialization until full setup)
        self.frame.after(100, self.update_ui)
    
    def update_ui(self):
        """Update the UI state based on application data."""
        # Update category dropdown
        categories = ["All"] + sorted([c.name for c in self.app.categories])
        self.category_combo.config(values=categories)
        
        # Apply current filters
        self.filter_bookmarks()
    
    def filter_bookmarks(self):
        """Filter bookmarks based on search term and filters."""
        # Get filter values
        search_term = self.search_var.get().lower()
        category = self.category_var.get()
        category = None if category == "All" else category
        
        rating = self.rating_var.get()
        min_rating = None if rating == "All" else int(rating)
        
        # Filter bookmarks
        self.filtered_bookmarks = self.app.link_controller.filter_bookmarks(
            search_term=search_term,
            category=category,
            min_rating=min_rating
        )
        
        # Reset pagination
        self.current_page = 0
        
        # Update display
        self.display_current_page()
    
    def display_current_page(self):
        """Display the current page of bookmarks."""
        # Clear current items
        self.tree.delete(*self.tree.get_children())
        
        # Calculate pagination
        page_size = self.page_size_var.get()
        total_pages = max(1, (len(self.filtered_bookmarks) + page_size - 1) // page_size)
        
        # Adjust current page if needed
        if self.current_page >= total_pages:
            self.current_page = total_pages - 1
        
        # Calculate start and end indices
        start_idx = self.current_page * page_size
        end_idx = min(start_idx + page_size, len(self.filtered_bookmarks))
        
        # Display bookmarks
        for bookmark in self.filtered_bookmarks[start_idx:end_idx]:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    bookmark.title,
                    bookmark.url,
                    bookmark.category,
                    bookmark.rating if bookmark.rating else ""
                ),
                tags=(bookmark.url,)  # Use URL as a tag for lookup
            )
        
        # Update page info
        self.page_info_var.set(f"Page {self.current_page + 1} of {total_pages} ({len(self.filtered_bookmarks)} bookmarks)")
        
        # Update status
        status_msg = f"Displaying {end_idx - start_idx} of {len(self.filtered_bookmarks)} bookmarks"
        
        # Update app's main window status if available
        if hasattr(self.app, 'main_window') and self.app.main_window:
            self.app.main_window.update_status(status_msg)
        
        # Also update local status label
        self.status_label.config(text=status_msg)
    
    def change_page(self, direction):
        """
        Change the current page.
        
        Args:
            direction (int): 1 for next page, -1 for previous page
        """
        page_size = self.page_size_var.get()
        total_pages = max(1, (len(self.filtered_bookmarks) + page_size - 1) // page_size)
        
        new_page = self.current_page + direction
        if 0 <= new_page < total_pages:
            self.current_page = new_page
            self.display_current_page()
    
    def update_page_size(self):
        """Update page size and refresh display."""
        self.display_current_page()
    
    def sort_column(self, column, reverse):
        """
        Sort the treeview by a column.
        
        Args:
            column (str): Column identifier
            reverse (bool): Sort in reverse order if True
        """
        if column == "rating":
            # Sort ratings as numbers
            def rating_key(bookmark):
                return bookmark.rating if bookmark.rating else -1
            
            self.filtered_bookmarks.sort(key=rating_key, reverse=reverse)
        else:
            # Sort other columns as strings
            def get_column_value(bookmark):
                if column == "title":
                    return bookmark.title.lower()
                elif column == "url":
                    return bookmark.url.lower()
                elif column == "category":
                    return bookmark.category.lower()
                return ""
            
            self.filtered_bookmarks.sort(key=get_column_value, reverse=reverse)
        
        # Display sorted bookmarks
        self.display_current_page()
        
        # Configure the column heading for next sort
        self.tree.heading(column, command=lambda: self.sort_column(column, not reverse))
    
    def on_select(self, event):
        """Handle treeview selection."""
        # No special handling needed for now
        pass
    
    def on_double_click(self, event):
        """Handle double-click on a bookmark."""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, "values")
            url = values[1]  # URL is the second column
            
            # Open URL in browser
            if url.startswith(('http://', 'https://')):
                webbrowser.open(url)
            else:
                webbrowser.open('https://' + url)
    
    def open_selected(self):
        """Open the selected bookmark in a web browser."""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, "values")
            url = values[1]  # URL is the second column
            
            # Open URL in browser
            if url.startswith(('http://', 'https://')):
                webbrowser.open(url)
            else:
                webbrowser.open('https://' + url)
    
    def add_bookmark_dialog(self):
        """Show dialog to add a new bookmark."""
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Add Bookmark")
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.geometry("400x200")
        
        # Create form
        ttk.Label(dialog, text="Title:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        title_entry = ttk.Entry(dialog, width=40)
        title_entry.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="URL:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        url_entry = ttk.Entry(dialog, width=40)
        url_entry.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="Category:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        category_var = tk.StringVar(value="Uncategorized")
        category_combo = ttk.Combobox(
            dialog,
            textvariable=category_var,
            values=sorted([c.name for c in self.app.categories]),
            width=38
        )
        category_combo.grid(row=2, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="Rating:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        rating_var = tk.StringVar(value="")
        rating_combo = ttk.Combobox(
            dialog,
            textvariable=rating_var,
            values=["", "1", "2", "3", "4", "5"],
            width=38
        )
        rating_combo.grid(row=3, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Function to add the bookmark
        def add_bookmark():
            title = title_entry.get().strip()
            url = url_entry.get().strip()
            category = category_var.get()
            rating_str = rating_var.get()
            
            if not title or not url:
                messagebox.showwarning("Missing Information", "Title and URL are required.")
                return
            
            # Add http:// prefix if missing
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Convert rating to int if provided
            rating = int(rating_str) if rating_str else None
            
            # Add bookmark
            self.app.link_controller.add_bookmark(
                url=url,
                title=title,
                category=category,
                rating=rating
            )
            
            # Close dialog
            dialog.destroy()
            
            # Update UI
            self.update_ui()
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Add", command=add_bookmark).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Make dialog resizable
        dialog.columnconfigure(1, weight=1)
        
        # Set focus to title entry
        title_entry.focus_set()
    
    def edit_bookmark(self):
        """Edit the selected bookmark."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a bookmark to edit.")
            return
        
        # Get selected bookmark
        item = selection[0]
        values = self.tree.item(item, "values")
        url = values[1]  # URL is the second column
        
        # Find bookmark object
        bookmark = None
        for b in self.app.bookmarks:
            if b.url == url:
                bookmark = b
                break
        
        if not bookmark:
            messagebox.showerror("Error", "Bookmark not found.")
            return
        
        # Create edit dialog
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Edit Bookmark")
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.geometry("400x200")
        
        # Create form
        ttk.Label(dialog, text="Title:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        title_var = tk.StringVar(value=bookmark.title)
        title_entry = ttk.Entry(dialog, width=40, textvariable=title_var)
        title_entry.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="URL:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        url_var = tk.StringVar(value=bookmark.url)
        url_entry = ttk.Entry(dialog, width=40, textvariable=url_var)
        url_entry.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="Category:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        category_var = tk.StringVar(value=bookmark.category)
        category_combo = ttk.Combobox(
            dialog,
            textvariable=category_var,
            values=sorted([c.name for c in self.app.categories]),
            width=38
        )
        category_combo.grid(row=2, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="Rating:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        rating_var = tk.StringVar(value=str(bookmark.rating) if bookmark.rating else "")
        rating_combo = ttk.Combobox(
            dialog,
            textvariable=rating_var,
            values=["", "1", "2", "3", "4", "5"],
            width=38
        )
        rating_combo.grid(row=3, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Function to update the bookmark
        def update_bookmark():
            title = title_var.get().strip()
            url = url_var.get().strip()
            category = category_var.get()
            rating_str = rating_var.get()
            
            if not title or not url:
                messagebox.showwarning("Missing Information", "Title and URL are required.")
                return
            
            # Add http:// prefix if missing
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Convert rating to int if provided
            rating = int(rating_str) if rating_str else None
            
            # Update bookmark
            self.app.link_controller.update_bookmark(
                bookmark,
                title=title,
                url=url,
                category=category,
                rating=rating
            )
            
            # Close dialog
            dialog.destroy()
            
            # Update UI
            self.update_ui()
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Update", command=update_bookmark).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Make dialog resizable
        dialog.columnconfigure(1, weight=1)
        
        # Set focus to title entry
        title_entry.focus_set()
    
    def delete_bookmark(self):
        """Delete the selected bookmark."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a bookmark to delete.")
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete the selected bookmark?"):
            return
        
        # Get selected bookmark
        item = selection[0]
        values = self.tree.item(item, "values")
        url = values[1]  # URL is the second column
        
        # Find bookmark object
        bookmark = None
        for b in self.app.bookmarks:
            if b.url == url:
                bookmark = b
                break
        
        if not bookmark:
            messagebox.showerror("Error", "Bookmark not found.")
            return
        
        # Delete bookmark
        if self.app.link_controller.delete_bookmark(bookmark):
            # Update UI
            self.update_ui()
            
            # Update status
            status_msg = "Bookmark deleted."
            self.status_label.config(text=status_msg)
            if hasattr(self.app, 'main_window') and self.app.main_window:
                self.app.main_window.update_status(status_msg)
    
    def bulk_categorize(self):
        """Categorize multiple selected bookmarks."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select bookmarks to categorize.")
            return
        
        # Ask for category
        categories = sorted([c.name for c in self.app.categories])
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Bulk Categorize")
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.geometry("300x100")
        
        ttk.Label(dialog, text="Select category:").pack(padx=10, pady=10)
        
        category_var = tk.StringVar(value=categories[0] if categories else "Uncategorized")
        category_combo = ttk.Combobox(
            dialog,
            textvariable=category_var,
            values=categories,
            width=30
        )
        category_combo.pack(padx=10, pady=5)
        
        # Function to categorize bookmarks
        def do_categorize():
            category = category_var.get()
            
            # Get selected bookmarks
            for item in selection:
                values = self.tree.item(item, "values")
                url = values[1]  # URL is the second column
                
                # Find bookmark object
                for bookmark in self.app.bookmarks:
                    if bookmark.url == url:
                        self.app.link_controller.update_bookmark(bookmark, category=category)
                        break
            
            # Close dialog
            dialog.destroy()
            
            # Update UI
            self.update_ui()
            
            # Update status
            status_msg = f"{len(selection)} bookmarks categorized as '{category}'."
            self.status_label.config(text=status_msg)
            if hasattr(self.app, 'main_window') and self.app.main_window:
                self.app.main_window.update_status(status_msg)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Categorize", command=do_categorize).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def bulk_delete(self):
        """Delete multiple selected bookmarks."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select bookmarks to delete.")
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {len(selection)} selected bookmarks?"):
            return
        
        # Delete bookmarks
        count = 0
        for item in selection:
            values = self.tree.item(item, "values")
            url = values[1]  # URL is the second column
            
            # Find bookmark object
            for bookmark in self.app.bookmarks[:]:  # Create a copy to safely modify during iteration
                if bookmark.url == url:
                    if self.app.link_controller.delete_bookmark(bookmark):
                        count += 1
                    break
        
        # Update UI
        self.update_ui()
        
        # Update status
        status_msg = f"{count} bookmarks deleted."
        self.status_label.config(text=status_msg)
        if hasattr(self.app, 'main_window') and self.app.main_window:
            self.app.main_window.update_status(status_msg)
    
    def reset_filters(self):
        """Reset all filters."""
        self.search_var.set("")
        self.category_var.set("All")
        self.rating_var.set("All")
        self.filter_bookmarks()