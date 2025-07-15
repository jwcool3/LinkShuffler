import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import webbrowser
from datetime import datetime

class CategoriesTab:
    """
    Categories tab view for the BookmarkShuffler application.
    """
    def __init__(self, app, parent):
        """
        Initialize the categories tab.
        
        Args:
            app: The main application instance
            parent: The parent widget (frame)
        """
        self.app = app
        self.parent = parent
        
        # Use the provided frame directly
        self.frame = parent
        
        # Current sort settings
        self.sort_column = "title"
        self.sort_reverse = False
        
        # Performance optimization variables
        self._current_category = None
        self._cached_bookmarks = {}
        self._sorted_bookmarks = []
        self._last_update_time = 0
        
        # Create top controls frame
        controls_frame = ttk.Frame(self.frame)
        controls_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Action buttons
        add_button = ttk.Button(controls_frame, text="Add Category", command=self.add_category)
        add_button.pack(side=tk.LEFT, padx=5)
        
        rename_button = ttk.Button(controls_frame, text="Rename Category", command=self.rename_category)
        rename_button.pack(side=tk.LEFT, padx=5)
        
        delete_button = ttk.Button(controls_frame, text="Delete Category", command=self.delete_category)
        delete_button.pack(side=tk.LEFT, padx=5)
        
        # Create split view with categories on left, bookmarks on right
        paned_window = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel - Categories
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=1)
        
        # Categories label
        ttk.Label(left_frame, text="Categories").pack(anchor=tk.W, padx=5, pady=5)
        
        # Categories listbox with scrollbar
        categories_frame = ttk.Frame(left_frame)
        categories_frame.pack(fill=tk.BOTH, expand=True)
        
        self.categories_listbox = tk.Listbox(categories_frame, selectmode=tk.SINGLE)
        self.categories_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        categories_scrollbar = ttk.Scrollbar(categories_frame, orient=tk.VERTICAL, command=self.categories_listbox.yview)
        self.categories_listbox.configure(yscrollcommand=categories_scrollbar.set)
        categories_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event with debouncing
        self.categories_listbox.bind("<<ListboxSelect>>", self._on_category_select_debounced)
        
        # Right panel - Bookmarks in category
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=2)
        
        # Bookmarks header frame
        bookmarks_header_frame = ttk.Frame(right_frame)
        bookmarks_header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Bookmarks label
        self.bookmarks_label = ttk.Label(bookmarks_header_frame, text="Bookmarks")
        self.bookmarks_label.pack(side=tk.LEFT, anchor=tk.W)
        
        # Sort controls
        sort_frame = ttk.Frame(bookmarks_header_frame)
        sort_frame.pack(side=tk.RIGHT)
        
        ttk.Label(sort_frame, text="Sort by:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.sort_var = tk.StringVar(value="title")
        sort_combo = ttk.Combobox(
            sort_frame,
            textvariable=self.sort_var,
            values=["title", "url", "rating", "date_added"],
            state="readonly",
            width=12
        )
        sort_combo.pack(side=tk.LEFT, padx=(0, 5))
        sort_combo.bind("<<ComboboxSelected>>", self.on_sort_change)
        
        # Sort order button
        self.sort_order_button = ttk.Button(
            sort_frame,
            text="↑",
            width=3,
            command=self.toggle_sort_order
        )
        self.sort_order_button.pack(side=tk.LEFT)
        
        # Bookmarks treeview with scrollbar
        bookmarks_frame = ttk.Frame(right_frame)
        bookmarks_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview with date column
        columns = ("title", "url", "rating", "date_added")
        self.bookmarks_tree = ttk.Treeview(bookmarks_frame, columns=columns, show="headings")
        
        # Define headings with sorting
        self.bookmarks_tree.heading("title", text="Title", command=lambda: self.sort_by_column("title"))
        self.bookmarks_tree.heading("url", text="URL", command=lambda: self.sort_by_column("url"))
        self.bookmarks_tree.heading("rating", text="Rating", command=lambda: self.sort_by_column("rating"))
        self.bookmarks_tree.heading("date_added", text="Date Added", command=lambda: self.sort_by_column("date_added"))
        
        # Set column widths
        self.bookmarks_tree.column("title", width=200, minwidth=150)
        self.bookmarks_tree.column("url", width=250, minwidth=150)
        self.bookmarks_tree.column("rating", width=50, minwidth=50)
        self.bookmarks_tree.column("date_added", width=100, minwidth=80)
        
        # Add scrollbar
        bookmarks_scrollbar = ttk.Scrollbar(bookmarks_frame, orient=tk.VERTICAL, command=self.bookmarks_tree.yview)
        self.bookmarks_tree.configure(yscrollcommand=bookmarks_scrollbar.set)
        bookmarks_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.bookmarks_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(bookmarks_frame, orient=tk.HORIZONTAL, command=self.bookmarks_tree.xview)
        self.bookmarks_tree.configure(xscrollcommand=h_scrollbar.set)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind double-click event for opening bookmarks
        self.bookmarks_tree.bind("<Double-1>", self.on_bookmark_double_click)
        
        # Bookmark actions frame
        bookmark_actions_frame = ttk.Frame(right_frame)
        bookmark_actions_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Open button
        open_button = ttk.Button(bookmark_actions_frame, text="Open", command=self.open_selected_bookmark)
        open_button.pack(side=tk.LEFT, padx=5)
        
        # Remove button (removes from category but doesn't delete)
        remove_button = ttk.Button(bookmark_actions_frame, text="Remove from Category", command=self.remove_from_category)
        remove_button.pack(side=tk.LEFT, padx=5)
        
        # Delete button
        delete_bookmark_button = ttk.Button(bookmark_actions_frame, text="Delete Bookmark", command=self.delete_selected_bookmark)
        delete_bookmark_button.pack(side=tk.LEFT, padx=5)
        
        # Move button (move to another category)
        move_button = ttk.Button(bookmark_actions_frame, text="Move to Category", command=self.move_to_category)
        move_button.pack(side=tk.LEFT, padx=5)
        
        # Update UI
        self.update_ui()
    
    def _on_category_select_debounced(self, event):
        """Debounced category selection handler to prevent excessive updates."""
        # Cancel any pending updates
        if hasattr(self, '_update_job'):
            self.frame.after_cancel(self._update_job)
        
        # Schedule the actual update
        self._update_job = self.frame.after(100, self.on_category_select)
    
    def _invalidate_cache(self):
        """Invalidate the bookmark cache when data changes."""
        self._cached_bookmarks.clear()
        self._sorted_bookmarks.clear()
    
    def update_ui(self):
        """Update the UI state based on application data."""
        # Invalidate cache when UI is updated
        self._invalidate_cache()
        
        # Update categories listbox
        self.categories_listbox.delete(0, tk.END)
        
        # Add categories to listbox
        for category in sorted([c.name for c in self.app.categories]):
            self.categories_listbox.insert(tk.END, category)
            
        # Clear bookmarks tree
        self.bookmarks_tree.delete(*self.bookmarks_tree.get_children())
        
        # Update bookmarks label
        self.bookmarks_label.config(text="Bookmarks")
    
    def on_category_select(self, event=None):
        """Handle category selection with caching and optimization."""
        selection = self.categories_listbox.curselection()
        if not selection:
            return
        
        # Get selected category
        category_name = self.categories_listbox.get(selection[0])
        
        # Update bookmarks label
        self.bookmarks_label.config(text=f"Bookmarks in '{category_name}'")
        
        # Create cache key that includes sort settings
        cache_key = f"{category_name}_{self.sort_column}_{self.sort_reverse}"
        
        # Check if this is the same category AND same sort settings (avoid unnecessary updates)
        if (self._current_category == category_name and 
            cache_key in self._cached_bookmarks):
            self._display_bookmarks_optimized(self._cached_bookmarks[cache_key])
            return
        
        self._current_category = category_name
        
        # Get bookmarks in category
        bookmarks = self.app.link_controller.get_bookmarks_by_category(category_name)
        
        # Sort bookmarks
        sorted_bookmarks = self.sort_bookmarks(bookmarks)
        
        # Cache the sorted bookmarks
        self._cached_bookmarks[cache_key] = sorted_bookmarks
        
        # Display bookmarks
        self._display_bookmarks_optimized(sorted_bookmarks)
        
        # Update status
        self.app.main_window.update_status(f"Category '{category_name}' has {len(bookmarks)} bookmarks")
    
    def _display_bookmarks_optimized(self, bookmarks):
        """Optimized bookmark display with batch operations."""
        # Clear current items
        self.bookmarks_tree.delete(*self.bookmarks_tree.get_children())
        
        # For very large datasets, consider virtual scrolling
        if len(bookmarks) > 1000:
            self._display_bookmarks_virtual(bookmarks)
        else:
            self._display_bookmarks_batch(bookmarks)
    
    def _display_bookmarks_batch(self, bookmarks):
        """Display bookmarks in batches to keep UI responsive."""
        batch_size = 100
        
        def insert_batch(start_idx):
            end_idx = min(start_idx + batch_size, len(bookmarks))
            
            # Prepare batch data
            batch_data = []
            for i in range(start_idx, end_idx):
                bookmark = bookmarks[i]
                
                # Get date added (handle both enhanced and regular bookmarks)
                date_str = "N/A"
                if hasattr(bookmark, 'date_added') and bookmark.date_added:
                    if isinstance(bookmark.date_added, datetime):
                        date_str = bookmark.date_added.strftime("%Y-%m-%d")
                    else:
                        date_str = str(bookmark.date_added)
                
                batch_data.append({
                    'values': (
                        bookmark.title,
                        bookmark.url,
                        bookmark.rating if bookmark.rating else "",
                        date_str
                    ),
                    'tags': (bookmark.url,)
                })
            
            # Insert batch
            for item_data in batch_data:
                self.bookmarks_tree.insert("", tk.END, values=item_data['values'], tags=item_data['tags'])
            
            # Schedule next batch if there are more items
            if end_idx < len(bookmarks):
                self.frame.after(1, lambda: insert_batch(end_idx))
        
        # Start inserting batches
        if bookmarks:
            insert_batch(0)
    
    def _display_bookmarks_virtual(self, bookmarks):
        """Virtual scrolling for very large datasets (placeholder for future implementation)."""
        # For now, just display first 1000 items with a warning
        self._display_bookmarks_batch(bookmarks[:1000])
        
        if len(bookmarks) > 1000:
            # Add a placeholder item to indicate more items
            self.bookmarks_tree.insert("", tk.END, values=(
                f"... and {len(bookmarks) - 1000} more items",
                "Use filters to narrow down results",
                "",
                ""
            ), tags=("placeholder",))
    
    def sort_bookmarks(self, bookmarks):
        """Sort bookmarks by the current sort column and order with caching."""
        # Create a cache key for this sort configuration
        cache_key = f"sort_{self.sort_column}_{self.sort_reverse}_{len(bookmarks)}"
        
        # Check if we have cached sorted bookmarks
        if hasattr(self, '_sort_cache') and cache_key in self._sort_cache:
            return self._sort_cache[cache_key]
        
        # Initialize sort cache if it doesn't exist
        if not hasattr(self, '_sort_cache'):
            self._sort_cache = {}
        
        # Sort bookmarks
        if self.sort_column == "title":
            sorted_bookmarks = sorted(bookmarks, key=lambda x: x.title.lower(), reverse=self.sort_reverse)
        elif self.sort_column == "url":
            sorted_bookmarks = sorted(bookmarks, key=lambda x: x.url.lower(), reverse=self.sort_reverse)
        elif self.sort_column == "rating":
            sorted_bookmarks = sorted(bookmarks, key=lambda x: x.rating or 0, reverse=self.sort_reverse)
        elif self.sort_column == "date_added":
            sorted_bookmarks = sorted(bookmarks, key=lambda x: getattr(x, 'date_added', datetime.min), reverse=self.sort_reverse)
        else:
            sorted_bookmarks = bookmarks
        
        # Cache the result
        self._sort_cache[cache_key] = sorted_bookmarks
        
        # Limit cache size to prevent memory issues
        if len(self._sort_cache) > 20:
            # Remove oldest entries
            keys_to_remove = list(self._sort_cache.keys())[:5]
            for key in keys_to_remove:
                del self._sort_cache[key]
        
        return sorted_bookmarks
    
    def sort_by_column(self, column):
        """Sort bookmarks by clicking on column header."""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        
        self.sort_var.set(column)
        self.update_sort_order_button()
        self.refresh_current_category()
    
    def on_sort_change(self, event=None):
        """Handle sort dropdown change."""
        self.sort_column = self.sort_var.get()
        self.sort_reverse = False
        self.update_sort_order_button()
        self.refresh_current_category()
    
    def toggle_sort_order(self):
        """Toggle sort order between ascending and descending."""
        self.sort_reverse = not self.sort_reverse
        self.update_sort_order_button()
        self.refresh_current_category()
    
    def update_sort_order_button(self):
        """Update the sort order button text."""
        self.sort_order_button.config(text="↓" if self.sort_reverse else "↑")
    
    def refresh_current_category(self):
        """Refresh the currently selected category display."""
        # Invalidate all caches to force refresh
        self._invalidate_cache()
        
        # Also clear sort cache
        if hasattr(self, '_sort_cache'):
            self._sort_cache.clear()
        
        # Force refresh by temporarily clearing current category
        current_category = self._current_category
        self._current_category = None
        
        # Trigger category selection refresh
        if current_category:
            # Find the category in the listbox and select it
            for i in range(self.categories_listbox.size()):
                if self.categories_listbox.get(i) == current_category:
                    self.categories_listbox.selection_clear(0, tk.END)
                    self.categories_listbox.selection_set(i)
                    break
            
            # Set current category back and refresh
            self._current_category = current_category
            self.on_category_select()
    
    def on_bookmark_double_click(self, event):
        """Handle double-click on bookmark to open it."""
        self.open_selected_bookmark()
    
    def open_selected_bookmark(self):
        """Open the selected bookmark in the default browser."""
        selection = self.bookmarks_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a bookmark to open.")
            return
        
        # Get the bookmark URL from the selected item
        item = selection[0]
        values = self.bookmarks_tree.item(item, "values")
        
        if values and len(values) > 1:
            url = values[1]  # URL is the second column
            
            # Skip placeholder items
            if url == "Use filters to narrow down results":
                return
            
            # Open URL in browser
            try:
                webbrowser.open(url)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open URL: {str(e)}")
    
    def get_selected_bookmark(self):
        """Get the bookmark object for the selected tree item."""
        selection = self.bookmarks_tree.selection()
        if not selection:
            return None
        
        # Get the bookmark URL from the selected item
        item = selection[0]
        values = self.bookmarks_tree.item(item, "values")
        
        if values and len(values) > 1:
            url = values[1]  # URL is the second column
            
            # Skip placeholder items
            if url == "Use filters to narrow down results":
                return None
            
            # Find the bookmark object
            for bookmark in self.app.bookmarks:
                if bookmark.url == url:
                    return bookmark
        
        return None
    
    def remove_from_category(self):
        """Remove the selected bookmark from its current category."""
        bookmark = self.get_selected_bookmark()
        if not bookmark:
            messagebox.showwarning("No Selection", "Please select a bookmark to remove.")
            return
        
        # Confirm removal
        if messagebox.askyesno("Confirm Removal", 
                              f"Remove '{bookmark.title}' from category '{bookmark.category}'?"):
            # Update bookmark category to Uncategorized
            self.app.link_controller.update_bookmark(bookmark, category="Uncategorized")
            
            # Refresh display
            self.refresh_current_category()
            
            # Update other tabs
            if hasattr(self.app, 'main_window'):
                self.app.main_window.update_ui()
    
    def delete_selected_bookmark(self):
        """Delete the selected bookmark entirely."""
        bookmark = self.get_selected_bookmark()
        if not bookmark:
            messagebox.showwarning("No Selection", "Please select a bookmark to delete.")
            return
        
        # Confirm deletion
        if messagebox.askyesno("Confirm Deletion", 
                              f"Permanently delete '{bookmark.title}'?"):
            # Delete bookmark
            self.app.link_controller.delete_bookmark(bookmark)
            
            # Refresh display
            self.refresh_current_category()
            
            # Update other tabs
            if hasattr(self.app, 'main_window'):
                self.app.main_window.update_ui()
    
    def move_to_category(self):
        """Move the selected bookmark to another category."""
        bookmark = self.get_selected_bookmark()
        if not bookmark:
            messagebox.showwarning("No Selection", "Please select a bookmark to move.")
            return
        
        # Get list of categories
        categories = [c.name for c in self.app.categories if c.name != bookmark.category]
        
        if not categories:
            messagebox.showinfo("No Categories", "No other categories available.")
            return
        
        # Show category selection dialog
        from tkinter import simpledialog
        
        class CategorySelectionDialog:
            def __init__(self, parent, categories):
                self.result = None
                
                # Create dialog
                self.dialog = tk.Toplevel(parent)
                self.dialog.title("Select Category")
                self.dialog.geometry("300x200")
                self.dialog.transient(parent)
                self.dialog.grab_set()
                
                # Category listbox
                ttk.Label(self.dialog, text="Select target category:").pack(pady=10)
                
                self.category_listbox = tk.Listbox(self.dialog, selectmode=tk.SINGLE)
                self.category_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
                
                for category in sorted(categories):
                    self.category_listbox.insert(tk.END, category)
                
                # Buttons
                button_frame = ttk.Frame(self.dialog)
                button_frame.pack(fill=tk.X, pady=10)
                
                ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
                ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.LEFT, padx=5)
                
                # Center dialog
                self.dialog.update_idletasks()
                x = (self.dialog.winfo_screenwidth() // 2) - (150)
                y = (self.dialog.winfo_screenheight() // 2) - (100)
                self.dialog.geometry(f"300x200+{x}+{y}")
            
            def ok_clicked(self):
                selection = self.category_listbox.curselection()
                if selection:
                    self.result = self.category_listbox.get(selection[0])
                self.dialog.destroy()
            
            def cancel_clicked(self):
                self.dialog.destroy()
        
        # Show dialog
        dialog = CategorySelectionDialog(self.frame, categories)
        self.frame.wait_window(dialog.dialog)
        
        if dialog.result:
            # Move bookmark to selected category
            self.app.link_controller.update_bookmark(bookmark, category=dialog.result)
            
            # Refresh display
            self.refresh_current_category()
            
            # Update other tabs
            if hasattr(self.app, 'main_window'):
                self.app.main_window.update_ui()
    
    def add_category(self):
        """Add a new category."""
        name = simpledialog.askstring("Add Category", "Enter category name:")
        if name:
            # Create new category
            self.app.link_controller._ensure_category_exists(name)
            
            # Update UI
            self.update_ui()
            
            # Update other tabs
            if hasattr(self.app, 'main_window'):
                self.app.main_window.update_ui()
    
    def rename_category(self):
        """Rename the selected category."""
        selection = self.categories_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a category to rename.")
            return
        
        old_name = self.categories_listbox.get(selection[0])
        
        if old_name == "Uncategorized":
            messagebox.showwarning("Cannot Rename", "Cannot rename the 'Uncategorized' category.")
            return
        
        new_name = simpledialog.askstring("Rename Category", f"Enter new name for '{old_name}':")
        if new_name and new_name != old_name:
            # Update all bookmarks in this category
            for bookmark in self.app.bookmarks:
                if bookmark.category == old_name:
                    bookmark.category = new_name
            
            # Update category object
            for category in self.app.categories:
                if category.name == old_name:
                    category.name = new_name
                    break
            
            # Invalidate cache
            self._invalidate_cache()
            
            # Update UI
            self.update_ui()
            
            # Update other tabs
            if hasattr(self.app, 'main_window'):
                self.app.main_window.update_ui()
    
    def delete_category(self):
        """Delete the selected category."""
        selection = self.categories_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a category to delete.")
            return
        
        category_name = self.categories_listbox.get(selection[0])
        
        if category_name == "Uncategorized":
            messagebox.showwarning("Cannot Delete", "Cannot delete the 'Uncategorized' category.")
            return
        
        # Count bookmarks in category
        bookmark_count = len(self.app.link_controller.get_bookmarks_by_category(category_name))
        
        # Confirm deletion
        message = f"Delete category '{category_name}'?"
        if bookmark_count > 0:
            message += f"\n{bookmark_count} bookmarks will be moved to 'Uncategorized'."
        
        if messagebox.askyesno("Confirm Deletion", message):
            # Move all bookmarks to Uncategorized
            for bookmark in self.app.bookmarks:
                if bookmark.category == category_name:
                    bookmark.category = "Uncategorized"
            
            # Remove category
            self.app.categories = [c for c in self.app.categories if c.name != category_name]
            
            # Invalidate cache
            self._invalidate_cache()
            
            # Update UI
            self.update_ui()
            
            # Update other tabs
            if hasattr(self.app, 'main_window'):
                self.app.main_window.update_ui()