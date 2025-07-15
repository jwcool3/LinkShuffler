import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import webbrowser
import sys
import os

# Add the parent directory to the path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.validation import validate_and_normalize_url

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
        
        # Configure column widths
        self.tree.column("title", width=300)
        self.tree.column("url", width=400)
        self.tree.column("category", width=150)
        self.tree.column("rating", width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click to edit
        self.tree.bind("<Double-1>", lambda e: self.edit_bookmark())
        
        # Create context menu
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Open Link", command=self.open_selected_link)
        self.context_menu.add_command(label="Edit", command=self.edit_bookmark)
        self.context_menu.add_command(label="Delete", command=self.delete_bookmark)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Bulk Categorize", command=self.bulk_categorize)
        self.context_menu.add_command(label="Bulk Delete", command=self.bulk_delete)
        
        # Bind right-click to context menu
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # Create bottom frame for controls
        bottom_frame = ttk.Frame(self.frame)
        bottom_frame.pack(fill=tk.X, pady=5, padx=10)
        
        # Action buttons
        ttk.Button(bottom_frame, text="Open Link", command=self.open_selected_link).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="Edit", command=self.edit_bookmark).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="Delete", command=self.delete_bookmark).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="Bulk Categorize", command=self.bulk_categorize).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="Bulk Delete", command=self.bulk_delete).pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = ttk.Label(bottom_frame, text="Ready")
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
        # Current sort column and direction
        self.sort_column_name = None
        self.sort_reverse = False
        
        # Initialize UI
        self.update_ui()
    
    def update_ui(self):
        """Update the UI with current data."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Update category filter
        categories = sorted([c.name for c in self.app.categories])
        self.category_combo['values'] = ["All"] + categories
        
        # Filter bookmarks
        self.filter_bookmarks()
    
    def filter_bookmarks(self):
        """Filter bookmarks based on current filters."""
        search_term = self.search_var.get().strip()
        category = self.category_var.get()
        rating = self.rating_var.get()
        
        # Convert rating to integer
        min_rating = None
        if rating != "All":
            min_rating = int(rating)
        
        # Get filtered bookmarks
        filtered_bookmarks = self.app.link_controller.filter_bookmarks(
            search_term=search_term if search_term else None,
            category=category if category != "All" else None,
            min_rating=min_rating
        )
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add filtered bookmarks
        for bookmark in filtered_bookmarks:
            rating_display = str(bookmark.rating) if bookmark.rating else ""
            self.tree.insert("", tk.END, values=(
                bookmark.title,
                bookmark.url,
                bookmark.category,
                rating_display
            ))
        
        # Update status
        total_count = len(self.app.bookmarks)
        filtered_count = len(filtered_bookmarks)
        self.status_label.config(text=f"Showing {filtered_count} of {total_count} bookmarks")
    
    def sort_column(self, column, reverse):
        """Sort treeview by column."""
        # Get all items
        items = [(self.tree.set(item, column), item) for item in self.tree.get_children()]
        
        # Sort items
        if column == "rating":
            # Handle rating column specially (empty values last)
            items.sort(key=lambda x: (x[0] == "", x[0]), reverse=reverse)
        else:
            items.sort(key=lambda x: x[0].lower(), reverse=reverse)
        
        # Rearrange items
        for index, (val, item) in enumerate(items):
            self.tree.move(item, '', index)
        
        # Update heading to show sort direction
        for col in ("title", "url", "category", "rating"):
            if col == column:
                direction = " ↓" if reverse else " ↑"
                self.tree.heading(col, text=col.title() + direction)
            else:
                self.tree.heading(col, text=col.title())
        
        # Update sort state
        self.sort_column_name = column
        self.sort_reverse = not reverse
        
        # Update heading command for next click
        self.tree.heading(column, command=lambda: self.sort_column(column, not reverse))
    
    def show_context_menu(self, event):
        """Show context menu on right-click."""
        # Select item under cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def open_selected_link(self):
        """Open the selected bookmark in a web browser."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a bookmark to open.")
            return
        
        item = selection[0]
        values = self.tree.item(item, "values")
        url = values[1]  # URL is the second column
        
        # Open URL in browser
        if url.startswith(('http://', 'https://')):
            webbrowser.open(url)
        else:
            webbrowser.open('https://' + url)
    
    def delete_bookmark(self):
        """Delete the selected bookmark."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a bookmark to delete.")
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete the selected bookmark?"):
            return
        
        item = selection[0]
        values = self.tree.item(item, "values")
        url = values[1]  # URL is the second column
        
        # Find bookmark object
        for bookmark in self.app.bookmarks:
            if bookmark.url == url:
                if self.app.link_controller.delete_bookmark(bookmark):
                    self.update_ui()
                    self.status_label.config(text="Bookmark deleted")
                    # Update other tabs if needed
                    if self.app.main_window:
                        self.app.main_window.update_status("Bookmark deleted")
                break
    
    def add_bookmark_dialog(self):
        """Show dialog to add a new bookmark."""
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Add Bookmark")
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.geometry("400x250")
        
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
        
        # URL validation status label
        validation_label = ttk.Label(dialog, text="", foreground="red")
        validation_label.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        
        # Function to validate URL as user types
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
        
        # Bind URL validation to entry
        url_entry.bind("<KeyRelease>", validate_url_input)
        
        # Function to add the bookmark
        def add_bookmark():
            url = url_entry.get().strip()
            title = title_entry.get().strip()
            category = category_var.get()
            rating = rating_var.get()
            
            if not url or not title:
                messagebox.showwarning("Invalid Input", "Please enter both URL and title.")
                return
            
            # Convert rating to integer if provided
            rating_int = None
            if rating and rating != "None":
                try:
                    rating_int = int(rating)
                except ValueError:
                    messagebox.showwarning("Invalid Rating", "Rating must be a number between 1 and 5.")
                    return
            
            # Create bookmark
            self.app.link_controller.create_bookmark(
                url=url,
                title=title,
                category=category,
                rating=rating_int
            )
            
            # Close dialog
            dialog.destroy()
            
            # Refresh UI
            self.update_ui()
            self.app.main_window.update_status(f"Bookmark added: {title}")
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
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
        dialog.geometry("400x250")
        
        # Create form with current values
        ttk.Label(dialog, text="Title:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        title_var = tk.StringVar(value=bookmark.title)
        title_entry = ttk.Entry(dialog, textvariable=title_var, width=40)
        title_entry.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="URL:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        url_var = tk.StringVar(value=bookmark.url)
        url_entry = ttk.Entry(dialog, textvariable=url_var, width=40)
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
        
        # URL validation status label
        validation_label = ttk.Label(dialog, text="", foreground="red")
        validation_label.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        
        # Function to validate URL as user types
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
        
        # Bind URL validation to entry
        url_entry.bind("<KeyRelease>", validate_url_input)
        
        # Function to update the bookmark
        def update_bookmark():
            title = title_var.get().strip()
            url = url_var.get().strip()
            category = category_var.get()
            rating_str = rating_var.get()
            
            if not title or not url:
                messagebox.showwarning("Missing Information", "Title and URL are required.")
                return
            
            # Validate and normalize URL
            is_valid, normalized_url, error_msg = validate_and_normalize_url(url)
            if not is_valid:
                messagebox.showerror("Invalid URL", f"URL validation failed: {error_msg}")
                return
            
            # Convert rating to int if provided
            rating = int(rating_str) if rating_str else None
            
            # Update bookmark
            self.app.link_controller.update_bookmark(
                bookmark,
                title=title,
                url=normalized_url,
                category=category,
                rating=rating
            )
            
            # Close dialog
            dialog.destroy()
            
            # Update UI
            self.update_ui()
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Update", command=update_bookmark).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Make dialog resizable
        dialog.columnconfigure(1, weight=1)
        
        # Set focus to title entry
        title_entry.focus_set()
    
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