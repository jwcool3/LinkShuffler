import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import webbrowser

class CategoriesTab:
    """
    Categories tab view for the BookmarkShuffler application.
    """
    def __init__(self, app, parent):
        """
        Initialize the categories tab.
        
        Args:
            app: The main application instance
            parent: The parent widget (notebook)
        """
        self.app = app
        self.parent = parent
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        
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
        
        # Bind selection event
        self.categories_listbox.bind("<<ListboxSelect>>", self.on_category_select)
        
        # Right panel - Bookmarks in category
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=2)
        
        # Bookmarks label
        self.bookmarks_label = ttk.Label(right_frame, text="Bookmarks")
        self.bookmarks_label.pack(anchor=tk.W, padx=5, pady=5)
        
        # Bookmarks treeview with scrollbar
        bookmarks_frame = ttk.Frame(right_frame)
        bookmarks_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ("title", "url", "rating")
        self.bookmarks_tree = ttk.Treeview(bookmarks_frame, columns=columns, show="headings")
        
        # Define headings
        self.bookmarks_tree.heading("title", text="Title")
        self.bookmarks_tree.heading("url", text="URL")
        self.bookmarks_tree.heading("rating", text="Rating")
        
        # Set column widths
        self.bookmarks_tree.column("title", width=200, minwidth=150)
        self.bookmarks_tree.column("url", width=300, minwidth=150)
        self.bookmarks_tree.column("rating", width=50, minwidth=50)
        
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
    
    def update_ui(self):
        """Update the UI state based on application data."""
        # Update categories listbox
        self.categories_listbox.delete(0, tk.END)
        
        # Add categories to listbox
        for category in sorted([c.name for c in self.app.categories]):
            self.categories_listbox.insert(tk.END, category)
            
        # Clear bookmarks tree
        self.bookmarks_tree.delete(*self.bookmarks_tree.get_children())
        
        # Update bookmarks label
        self.bookmarks_label.config(text="Bookmarks")
    
    def on_category_select(self, event):
        """Handle category selection."""
        selection = self.categories_listbox.curselection()
        if not selection:
            return
        
        # Get selected category
        category_name = self.categories_listbox.get(selection[0])
        
        # Update bookmarks label
        self.bookmarks_label.config(text=f"Bookmarks in '{category_name}'")
        
        # Clear current items
        self.bookmarks_tree.delete(*self.bookmarks_tree.get_children())
        
        # Get bookmarks in category
        bookmarks = self.app.link_controller.get_bookmarks_by_category(category_name)
        
        # Display bookmarks
        for bookmark in bookmarks:
            self.bookmarks_tree.insert(
                "",
                tk.END,
                values=(
                    bookmark.title,
                    bookmark.url,
                    bookmark.rating if bookmark.rating else ""
                ),
                tags=(bookmark.url,)  # Use URL as a tag for lookup
            )
        
        # Update status
        self.app.main_window.update_status(f"Category '{category_name}' has {len(bookmarks)} bookmarks")
    
    def on_bookmark_double_click(self, event):
        """Handle double-click on a bookmark."""
        selection = self.bookmarks_tree.selection()
        if selection:
            item = selection[0]
            values = self.bookmarks_tree.item(item, "values")
            url = values[1]  # URL is the second column
            
            # Open URL in browser
            if url.startswith(('http://', 'https://')):
                webbrowser.open(url)
            else:
                webbrowser.open('https://' + url)
    
    def open_selected_bookmark(self):
        """Open the selected bookmark in a web browser."""
        selection = self.bookmarks_tree.selection()
        if selection:
            item = selection[0]
            values = self.bookmarks_tree.item(item, "values")
            url = values[1]  # URL is the second column
            
            # Open URL in browser
            if url.startswith(('http://', 'https://')):
                webbrowser.open(url)
            else:
                webbrowser.open('https://' + url)
    
    def add_category(self):
        """Add a new category."""
        category_name = simpledialog.askstring("Add Category", "Enter category name:")
        if not category_name:
            return
        
        # Check if category already exists
        if any(c.name == category_name for c in self.app.categories):
            messagebox.showwarning("Category Exists", f"Category '{category_name}' already exists.")
            return
        
        # Create category
        self.app.link_controller._ensure_category_exists(category_name)
        
        # Update UI
        self.update_ui()
        self.app.main_window.update_status(f"Category '{category_name}' created")
    
    def rename_category(self):
        """Rename the selected category."""
        selection = self.categories_listbox.curselection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a category to rename.")
            return
        
        # Get selected category
        old_name = self.categories_listbox.get(selection[0])
        
        # Prevent renaming "Uncategorized"
        if old_name == "Uncategorized":
            messagebox.showwarning("Cannot Rename", "The 'Uncategorized' category cannot be renamed.")
            return
        
        # Ask for new name
        new_name = simpledialog.askstring("Rename Category", "Enter new category name:", initialvalue=old_name)
        if not new_name or new_name == old_name:
            return
        
        # Check if new name already exists
        if any(c.name == new_name for c in self.app.categories):
            messagebox.showwarning("Category Exists", f"Category '{new_name}' already exists.")
            return
        
        # Find category object
        category = None
        for c in self.app.categories:
            if c.name == old_name:
                category = c
                break
        
        if not category:
            messagebox.showerror("Error", "Category not found.")
            return
        
        # Update all bookmarks in this category
        for bookmark in category.bookmarks[:]:  # Create a copy to safely modify during iteration
            self.app.link_controller.update_bookmark(bookmark, category=new_name)
        
        # Update category name
        category.name = new_name
        
        # Update UI
        self.update_ui()
        self.app.main_window.update_status(f"Category renamed to '{new_name}'")
    
    def delete_category(self):
        """Delete the selected category."""
        selection = self.categories_listbox.curselection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a category to delete.")
            return
        
        # Get selected category
        category_name = self.categories_listbox.get(selection[0])
        
        # Prevent deleting "Uncategorized"
        if category_name == "Uncategorized":
            messagebox.showwarning("Cannot Delete", "The 'Uncategorized' category cannot be deleted.")
            return
        
        # Find category object
        category = None
        for c in self.app.categories:
            if c.name == category_name:
                category = c
                break
        
        if not category:
            messagebox.showerror("Error", "Category not found.")
            return
        
        # Check if category has bookmarks
        if category.bookmarks:
            # Ask what to do with bookmarks
            dialog = tk.Toplevel(self.app.root)
            dialog.title("Delete Category")
            dialog.transient(self.app.root)
            dialog.grab_set()
            dialog.geometry("400x150")
            
            ttk.Label(
                dialog,
                text=f"Category '{category_name}' has {len(category.bookmarks)} bookmarks.\nWhat would you like to do with them?"
            ).pack(padx=10, pady=10)
            
            action_var = tk.StringVar(value="move")
            move_radio = ttk.Radiobutton(dialog, text="Move to 'Uncategorized'", variable=action_var, value="move")
            move_radio.pack(anchor=tk.W, padx=10)
            
            delete_radio = ttk.Radiobutton(dialog, text="Delete bookmarks", variable=action_var, value="delete")
            delete_radio.pack(anchor=tk.W, padx=10)
            
            def on_confirm():
                action = action_var.get()
                
                if action == "move":
                    # Move bookmarks to Uncategorized
                    for bookmark in category.bookmarks[:]:  # Create a copy to safely modify during iteration
                        self.app.link_controller.update_bookmark(bookmark, category="Uncategorized")
                else:
                    # Delete bookmarks
                    for bookmark in category.bookmarks[:]:  # Create a copy to safely modify during iteration
                        self.app.link_controller.delete_bookmark(bookmark)
                
                # Remove category
                self.app.categories.remove(category)
                
                # Update UI
                dialog.destroy()
                self.update_ui()
                self.app.main_window.update_status(f"Category '{category_name}' deleted")
            
            # Buttons
            button_frame = ttk.Frame(dialog)
            button_frame.pack(pady=10)
            
            ttk.Button(button_frame, text="Confirm", command=on_confirm).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        else:
            # No bookmarks, just confirm deletion
            if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the category '{category_name}'?"):
                # Remove category
                self.app.categories.remove(category)
                
                # Update UI
                self.update_ui()
                self.app.main_window.update_status(f"Category '{category_name}' deleted")
    
    def remove_from_category(self):
        """Remove selected bookmark from the current category."""
        # Get selected bookmark
        selection = self.bookmarks_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a bookmark to remove from the category.")
            return
        
        # Get selected category
        category_selection = self.categories_listbox.curselection()
        if not category_selection:
            messagebox.showinfo("No Category", "Please select a category first.")
            return
        
        category_name = self.categories_listbox.get(category_selection[0])
        
        # Prevent removing from "Uncategorized"
        if category_name == "Uncategorized":
            messagebox.showwarning("Cannot Remove", "Bookmarks cannot be removed from the 'Uncategorized' category.")
            return
        
        # Get selected bookmark
        item = selection[0]
        values = self.bookmarks_tree.item(item, "values")
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
        
        # Move to Uncategorized
        self.app.link_controller.update_bookmark(bookmark, category="Uncategorized")
        
        # Update UI
        self.update_ui()
        
        # Re-select the category to update the view
        self.categories_listbox.selection_set(category_selection)
        self.on_category_select(None)
        
        self.app.main_window.update_status(f"Bookmark removed from category '{category_name}'")
    
    def delete_selected_bookmark(self):
        """Delete the selected bookmark."""
        selection = self.bookmarks_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a bookmark to delete.")
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete the selected bookmark?"):
            return
        
        # Get selected bookmark
        item = selection[0]
        values = self.bookmarks_tree.item(item, "values")
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
            # Get selected category to restore selection after update
            category_selection = self.categories_listbox.curselection()
            
            # Update UI
            self.update_ui()
            
            # Re-select the category
            if category_selection:
                self.categories_listbox.selection_set(category_selection)
                self.on_category_select(None)
            
            self.app.main_window.update_status("Bookmark deleted.")
    
    def move_to_category(self):
        """Move selected bookmark to another category."""
        # Get selected bookmark
        selection = self.bookmarks_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a bookmark to move.")
            return
        
        # Get selected category
        category_selection = self.categories_listbox.curselection()
        if not category_selection:
            messagebox.showinfo("No Category", "Please select a category first.")
            return
        
        current_category = self.categories_listbox.get(category_selection[0])
        
        # Get selected bookmark
        item = selection[0]
        values = self.bookmarks_tree.item(item, "values")
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
        
        # Show dialog to select target category
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Move to Category")
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.geometry("300x150")
        
        ttk.Label(
            dialog,
            text=f"Select destination category for bookmark:"
        ).pack(padx=10, pady=10)
        
        # Get all categories except current one
        category_names = [c.name for c in self.app.categories if c.name != current_category]
        
        category_var = tk.StringVar()
        if category_names:
            category_var.set(category_names[0])
        
        category_combo = ttk.Combobox(
            dialog,
            textvariable=category_var,
            values=category_names,
            state="readonly",
            width=30
        )
        category_combo.pack(padx=10, pady=5)
        
        def on_move():
            target_category = category_var.get()
            
            # Move bookmark
            self.app.link_controller.update_bookmark(bookmark, category=target_category)
            
            # Close dialog
            dialog.destroy()
            
            # Update UI
            self.on_category_select(None)  # Refresh current category view
            
            self.app.main_window.update_status(f"Bookmark moved to category '{target_category}'")
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Move", command=on_move).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)