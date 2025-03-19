import tkinter as tk
from tkinter import ttk
from views.home_tab import HomeTab
from views.manage_tab import ManageTab
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
        
        # Create tabs
        self.home_tab = HomeTab(self.app, self.notebook)
        self.manage_tab = ManageTab(self.app, self.notebook)
        self.categories_tab = CategoriesTab(self.app, self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.home_tab.frame, text="Home")
        self.notebook.add(self.manage_tab.frame, text="Manage Links")
        self.notebook.add(self.categories_tab.frame, text="Categories")
        
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
        """Set up custom styles for ttk widgets."""
        self.style.configure("TButton", padding=6, relief="flat", background="#ccc")
        self.style.configure("TNotebook", background="#f0f0f0")
        self.style.configure("TNotebook.Tab", padding=[10, 2], font=('Arial', 10))
        self.style.configure("Treeview", font=('Arial', 10))
        self.style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
    
    def setup_menu(self):
        """Set up the application menu."""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Load HTML Bookmarks", command=self.load_html_callback)
        file_menu.add_command(label="Load JSON Data", command=self.load_data_callback)
        file_menu.add_command(label="Save Data", command=self.save_data_callback)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Add Bookmark", command=self.new_bookmark_callback)
        edit_menu.add_command(label="Detect Keywords", command=self.detect_keywords_callback)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Home", command=lambda: self.notebook.select(0))
        view_menu.add_command(label="Manage Links", command=lambda: self.notebook.select(1))
        view_menu.add_command(label="Categories", command=lambda: self.notebook.select(2))
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def update_ui(self):
        """Update all UI components."""
        self.home_tab.update_ui()
        self.manage_tab.update_ui()
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
    
    def new_bookmark_callback(self, event=None):
        """Callback for adding a new bookmark."""
        self.manage_tab.add_bookmark_dialog()
    
    def detect_keywords_callback(self):
        """Callback for detecting keywords."""
        self.app.keyword_controller.auto_categorize_bookmarks()
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