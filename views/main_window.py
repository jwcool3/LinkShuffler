import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
from views.home_tab import HomeTab
from views.manage_tab import ManageTab
from views.enhanced_manage_tab import EnhancedManageTab
from views.categories_tab import CategoriesTab

class MainWindow:
    """
    Main window for the BookmarkShuffler application.
    """
    def __init__(self, app):
        """
        Initialize the main window.
        
        Args:
            app: The main application instance
        """
        self.app = app
        self.root = app.root
        
        # Enhanced mode flag
        self.enhanced_mode = False
        
        # Apply a theme
        self.style = ttk.Style()
        available_themes = self.style.theme_names()
        if 'clam' in available_themes:
            self.style.theme_use('clam')
        
        # Custom styles
        self.setup_styles()
        
        # Create the main notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Create tab frames
        home_frame = ttk.Frame(self.notebook)
        manage_frame = ttk.Frame(self.notebook)
        categories_frame = ttk.Frame(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(home_frame, text="Home")
        self.notebook.add(manage_frame, text="Manage Links")
        self.notebook.add(categories_frame, text="Categories")
        
        # Create tabs
        self.home_tab = HomeTab(self.app, home_frame)
        self.manage_tab = ManageTab(self.app, manage_frame)
        self.enhanced_manage_tab = None  # Will be created when needed
        self.categories_tab = CategoriesTab(self.app, categories_frame)
        
        # Store frame references
        self.manage_frame = manage_frame
        
        # Create status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Set up menu
        self.setup_menu()
        
        # Bind events
        self.root.bind("<Control-s>", lambda e: self.app.file_controller.save_data())
        self.root.bind("<Control-o>", lambda e: self.load_data_callback())
        self.root.bind("<Control-n>", lambda e: self.new_bookmark_callback())
        
        # Configure grid weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
    
    def setup_styles(self):
        """Set up custom styles for the application."""
        # Configure custom styles here if needed
        pass
    
    def setup_menu(self):
        """Set up the application menu."""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Load HTML Bookmarks", command=self.load_html_callback)
        file_menu.add_command(label="Load JSON Data", command=self.load_data_callback)
        file_menu.add_separator()
        file_menu.add_command(label="Save Data", command=self.save_data_callback)
        file_menu.add_separator()
        file_menu.add_command(label="Export to CSV", command=self.export_csv_callback)
        file_menu.add_command(label="Import from CSV", command=self.import_csv_callback)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Add Bookmark", command=self.new_bookmark_callback)
        edit_menu.add_separator()
        edit_menu.add_command(label="Detect Keywords", command=self.detect_keywords_callback)
        edit_menu.add_command(label="Smart Categorization", command=self.smart_categorization_callback)
        edit_menu.add_command(label="Quick Auto-Categorize", command=self.quick_auto_categorize_callback)
        edit_menu.add_separator()
        edit_menu.add_command(label="Find Duplicates", command=self.find_duplicates_callback)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Auto-save Settings", command=self.auto_save_settings_callback)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Home", command=lambda: self.notebook.select(0))
        view_menu.add_command(label="Manage Links", command=lambda: self.notebook.select(1))
        view_menu.add_command(label="Categories", command=lambda: self.notebook.select(2))
        view_menu.add_separator()
        view_menu.add_command(label="Toggle Enhanced Mode", command=self.toggle_enhanced_mode)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Preferences", command=self.show_preferences)
        settings_menu.add_separator()
        settings_menu.add_command(label="Reset to Defaults", command=self.reset_settings)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        self.root.config(menu=menubar)
    
    def toggle_enhanced_mode(self):
        """Toggle between original and enhanced manage tab"""
        self.enhanced_mode = not self.enhanced_mode
        
        # Clear the manage frame
        for widget in self.manage_frame.winfo_children():
            widget.destroy()
        
        if self.enhanced_mode:
            # Create enhanced manage tab
            self.enhanced_manage_tab = EnhancedManageTab(self.app, self.manage_frame)
            self.manage_tab = None  # Clear reference to original tab
            self.update_status("Enhanced mode enabled - Advanced search, sort, and grouping available")
        else:
            # Create original manage tab
            self.manage_tab = ManageTab(self.app, self.manage_frame)
            self.enhanced_manage_tab = None  # Clear reference to enhanced tab
            self.update_status("Standard mode enabled")
    
    def get_current_manage_tab(self):
        """Get the currently active manage tab"""
        return self.enhanced_manage_tab if self.enhanced_mode else self.manage_tab

    def update_ui(self):
        """Update all UI components."""
        if hasattr(self, 'home_tab') and self.home_tab:
            self.home_tab.update_ui()
        
        # Update the current manage tab
        current_manage_tab = self.get_current_manage_tab()
        if current_manage_tab:
            current_manage_tab.update_ui()
        
        if hasattr(self, 'categories_tab') and self.categories_tab:
            self.categories_tab.update_ui()
        
        self.update_status(f"Loaded {len(self.app.bookmarks)} bookmarks in {len(self.app.categories)} categories")
    
    def update_status(self, message):
        """
        Update the status bar message.
        
        Args:
            message (str): The status message to display
        """
        self.status_var.set(message)
    
    # Callback methods
    def load_html_callback(self):
        """Callback for loading HTML bookmarks."""
        bookmarks = self.app.file_controller.load_html_bookmarks()
        if bookmarks:
            self.app.bookmarks = bookmarks
            self.update_ui()
    
    def load_data_callback(self, event=None):
        """Callback for loading JSON data."""
        result = self.app.file_controller.load_data()
        if result:
            self.app.bookmarks, self.app.categories = result
            self.app._ensure_uncategorized_exists()
            self.update_ui()
    
    def save_data_callback(self, event=None):
        """Callback for saving data."""
        self.app.file_controller.save_data()
    
    def export_csv_callback(self):
        """Callback for exporting bookmarks to CSV."""
        if not self.app.bookmarks:
            messagebox.showwarning("No Bookmarks", "No bookmarks to export.")
            return
        
        success = self.app.file_controller.export_to_csv()
        if success:
            self.update_status("Bookmarks exported to CSV successfully")
    
    def import_csv_callback(self):
        """Callback for importing bookmarks from CSV."""
        bookmarks = self.app.file_controller.import_from_csv()
        if bookmarks:
            # Add imported bookmarks to existing ones
            for bookmark in bookmarks:
                # Check if bookmark already exists
                exists = any(b.url == bookmark.url for b in self.app.bookmarks)
                if not exists:
                    self.app.bookmarks.append(bookmark)
                    # Add to appropriate category
                    self.app.link_controller._ensure_category_exists(bookmark.category)
                    for cat in self.app.categories:
                        if cat.name == bookmark.category:
                            cat.add_bookmark(bookmark)
                            break
            
            self.update_ui()
            self.update_status(f"Imported {len(bookmarks)} bookmarks from CSV")
    
    def find_duplicates_callback(self):
        """Callback for finding duplicate bookmarks."""
        duplicates = self.app.file_controller.find_duplicates()
        
        if not duplicates:
            messagebox.showinfo("No Duplicates", "No duplicate bookmarks found.")
            return
        
        # Show duplicates dialog
        self.show_duplicates_dialog(duplicates)
    
    def show_duplicates_dialog(self, duplicates):
        """Show dialog with duplicate bookmarks."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Duplicate Bookmarks Found")
        dialog.geometry("800x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create header
        header_frame = ttk.Frame(dialog)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(
            header_frame,
            text=f"Found {len(duplicates)} potential duplicate pairs:",
            font=("Arial", 12, "bold")
        ).pack(anchor=tk.W)
        
        # Create treeview for duplicates
        tree_frame = ttk.Frame(dialog)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("title1", "url1", "title2", "url2", "reason")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        # Define headings
        tree.heading("title1", text="Title 1")
        tree.heading("url1", text="URL 1")
        tree.heading("title2", text="Title 2")
        tree.heading("url2", text="URL 2")
        tree.heading("reason", text="Reason")
        
        # Configure column widths
        tree.column("title1", width=150)
        tree.column("url1", width=200)
        tree.column("title2", width=150)
        tree.column("url2", width=200)
        tree.column("reason", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate tree with duplicates
        for bookmark1, bookmark2, reason in duplicates:
            tree.insert("", tk.END, values=(
                bookmark1.title,
                bookmark1.url,
                bookmark2.title,
                bookmark2.url,
                reason
            ))
        
        # Button frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        def delete_selected():
            """Delete selected duplicate."""
            selection = tree.selection()
            if not selection:
                messagebox.showinfo("No Selection", "Please select a duplicate pair to resolve.")
                return
            
            item = selection[0]
            values = tree.item(item, "values")
            url1, url2 = values[1], values[3]
            
            # Show dialog to choose which one to delete
            choice_dialog = tk.Toplevel(dialog)
            choice_dialog.title("Choose Bookmark to Delete")
            choice_dialog.geometry("400x200")
            choice_dialog.transient(dialog)
            choice_dialog.grab_set()
            
            ttk.Label(choice_dialog, text="Which bookmark would you like to delete?").pack(pady=10)
            
            choice_var = tk.StringVar(value="first")
            ttk.Radiobutton(choice_dialog, text=f"First: {values[0]}", variable=choice_var, value="first").pack(anchor=tk.W, padx=20)
            ttk.Radiobutton(choice_dialog, text=f"Second: {values[2]}", variable=choice_var, value="second").pack(anchor=tk.W, padx=20)
            
            def confirm_delete():
                url_to_delete = url1 if choice_var.get() == "first" else url2
                
                # Find and delete bookmark
                for bookmark in self.app.bookmarks[:]:
                    if bookmark.url == url_to_delete:
                        self.app.link_controller.delete_bookmark(bookmark)
                        break
                
                # Remove from tree
                tree.delete(item)
                choice_dialog.destroy()
                
                # Update UI
                self.update_ui()
                messagebox.showinfo("Success", "Duplicate bookmark deleted.")
            
            ttk.Button(choice_dialog, text="Delete", command=confirm_delete).pack(side=tk.LEFT, padx=10, pady=10)
            ttk.Button(choice_dialog, text="Cancel", command=choice_dialog.destroy).pack(side=tk.LEFT, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Delete Selected", command=delete_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def auto_save_settings_callback(self):
        """Show auto-save settings dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Auto-save Settings")
        dialog.geometry("300x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Auto-save enabled checkbox
        auto_save_var = tk.BooleanVar(value=self.app.auto_save_enabled)
        ttk.Checkbutton(
            dialog,
            text="Enable auto-save",
            variable=auto_save_var
        ).pack(pady=10)
        
        # Auto-save interval
        ttk.Label(dialog, text="Auto-save interval (minutes):").pack(pady=5)
        
        interval_var = tk.IntVar(value=self.app.auto_save_interval // 60000)
        interval_spin = ttk.Spinbox(
            dialog,
            from_=1,
            to=60,
            textvariable=interval_var,
            width=10
        )
        interval_spin.pack(pady=5)
        
        def apply_settings():
            self.app.auto_save_enabled = auto_save_var.get()
            self.app.set_auto_save_interval(interval_var.get())
            
            if self.app.auto_save_enabled:
                self.app.schedule_auto_save()
            
            dialog.destroy()
            self.update_status("Auto-save settings updated")
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Apply", command=apply_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def new_bookmark_callback(self, event=None):
        """Callback for adding a new bookmark."""
        current_tab = self.get_current_manage_tab()
        if current_tab:
            if hasattr(current_tab, 'add_bookmark_dialog'):
                current_tab.add_bookmark_dialog()
            elif hasattr(current_tab, 'add_bookmark'):
                current_tab.add_bookmark()
        else:
            # Fallback - create a simple dialog
            messagebox.showinfo("Add Bookmark", "Please switch to the Manage Links tab to add bookmarks.")
    
    def detect_keywords_callback(self):
        """Callback for detecting keywords."""
        self.app.keyword_controller.auto_categorize_bookmarks()
        self.update_ui()
    
    def smart_categorization_callback(self):
        """Callback for smart categorization."""
        self.app.enhanced_keyword_controller.analyze_bookmarks_intelligent()
        self.update_ui()
    
    def quick_auto_categorize_callback(self):
        """Callback for quick auto-categorization."""
        self.app.enhanced_keyword_controller.quick_auto_categorize()
        self.update_ui()
    
    def show_about(self):
        """Show the about dialog."""
        about_win = tk.Toplevel(self.root)
        about_win.title("About BookmarkShuffler")
        about_win.geometry("300x200")
        about_win.resizable(False, False)
        about_win.transient(self.root)
        about_win.grab_set()
        
        ttk.Label(
            about_win,
            text="BookmarkShuffler",
            font=("Arial", 16, "bold")
        ).pack(pady=10)
        
        ttk.Label(
            about_win,
            text="A bookmark management application",
            font=("Arial", 10)
        ).pack()
        
        ttk.Label(
            about_win,
            text="Version 2.0",
            font=("Arial", 10)
        ).pack(pady=5)
        
        ttk.Button(
            about_win,
            text="OK",
            command=about_win.destroy
        ).pack(pady=20)
    
    def show_preferences(self):
        """Show preferences dialog"""
        if hasattr(self.app, 'config_manager'):
            from utils.config_manager import SettingsDialog
            dialog = SettingsDialog(self.root, self.app.config_manager)
            self.root.wait_window(dialog.dialog)
            
            # Apply any changes that affect the UI
            self.apply_config_changes()
        else:
            messagebox.showinfo("Settings", "Settings not available in this version.")
    
    def reset_settings(self):
        """Reset settings to defaults"""
        if hasattr(self.app, 'config_manager'):
            if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
                self.app.config_manager.reset_to_defaults()
                self.apply_config_changes()
                messagebox.showinfo("Settings Reset", "Settings have been reset to defaults. Please restart the application for all changes to take effect.")
        else:
            messagebox.showinfo("Settings", "Settings not available in this version.")
    
    def apply_config_changes(self):
        """Apply configuration changes to the UI"""
        if hasattr(self.app, 'config'):
            config = self.app.config
            
            # Apply theme
            try:
                style = ttk.Style()
                style.theme_use(config.theme)
            except tk.TclError:
                pass
            
            # Apply font settings
            try:
                # Apply font settings to various widgets
                default_font = tkfont.nametofont("TkDefaultFont")
                default_font.configure(size=config.font_size)
            except Exception:
                pass
            
            # Update enhanced mode if needed
            if config.enhanced_mode_default != self.enhanced_mode:
                self.toggle_enhanced_mode()
            
            # Refresh the current tab
            self.update_ui()
    
    def refresh_all_tabs(self):
        """Refresh all tabs to reflect changes."""
        # Update home tab
        if hasattr(self, 'home_tab'):
            self.home_tab.update_ui()
        
        # Update manage tab
        if hasattr(self, 'manage_tab'):
            self.manage_tab.update_ui()
        
        # Update categories tab
        if hasattr(self, 'categories_tab'):
            self.categories_tab.update_ui()
        
        # Update enhanced manage tab if it exists
        if hasattr(self, 'enhanced_manage_tab'):
            self.enhanced_manage_tab.update_ui()
        
        # Update main UI
        self.update_ui()