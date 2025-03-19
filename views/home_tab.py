import tkinter as tk
from tkinter import ttk
import webbrowser

class HomeTab:
    """
    Home tab view for the BookmarkShuffler application.
    """
    def __init__(self, app, parent):
        """
        Initialize the home tab.
        
        Args:
            app: The main application instance
            parent: The parent widget (notebook)
        """
        self.app = app
        self.parent = parent
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        
        # Create welcome header
        welcome_frame = ttk.Frame(self.frame)
        welcome_frame.pack(fill=tk.X, pady=20, padx=20)
        
        ttk.Label(
            welcome_frame,
            text="Welcome to BookmarkShuffler",
            font=("Arial", 16, "bold")
        ).pack(anchor=tk.W)
        
        ttk.Label(
            welcome_frame,
            text="Discover your forgotten bookmarks!",
            font=("Arial", 12)
        ).pack(anchor=tk.W)
        
        # Create button frame
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill=tk.X, pady=10, padx=20)
        
        # Load bookmarks button
        self.load_button = ttk.Button(
            button_frame,
            text="Load Bookmarks File",
            command=self.app.main_window.load_html_callback
        )
        self.load_button.pack(side=tk.LEFT, padx=5)
        
        # Detect keywords button
        self.keyword_button = ttk.Button(
            button_frame,
            text="Detect Keywords & Categorize",
            command=self.app.main_window.detect_keywords_callback
        )
        self.keyword_button.pack(side=tk.LEFT, padx=5)
        
        # Shuffle links button
        self.shuffle_button = ttk.Button(
            button_frame,
            text="Shuffle Links",
            command=self.shuffle_links
        )
        self.shuffle_button.pack(side=tk.LEFT, padx=5)
        
        # Display options frame
        options_frame = ttk.LabelFrame(self.frame, text="Shuffle Options")
        options_frame.pack(fill=tk.X, pady=10, padx=20)
        
        # Category filter
        ttk.Label(options_frame, text="Category:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.category_var = tk.StringVar(value="All")
        self.category_combo = ttk.Combobox(
            options_frame,
            textvariable=self.category_var,
            state="readonly",
            width=20
        )
        self.category_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Number of links to show
        ttk.Label(options_frame, text="Number of Links:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        
        self.num_links_var = tk.IntVar(value=5)
        self.num_links_spin = ttk.Spinbox(
            options_frame,
            from_=1,
            to=100,
            textvariable=self.num_links_var,
            width=5
        )
        self.num_links_spin.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        # Minimum rating filter
        ttk.Label(options_frame, text="Min. Rating:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        
        self.rating_var = tk.StringVar(value="Any")
        self.rating_combo = ttk.Combobox(
            options_frame,
            textvariable=self.rating_var,
            values=["Any", "1", "2", "3", "4", "5"],
            state="readonly",
            width=5
        )
        self.rating_combo.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.frame, text="Shuffled Links")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=20)
        
        # Scrollable text widget for results
        self.results_text = tk.Text(
            results_frame,
            wrap=tk.WORD,
            cursor="arrow",
            height=15
        )
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add scrollbar to text widget
        scrollbar = ttk.Scrollbar(results_frame, command=self.results_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.config(yscrollcommand=scrollbar.set)
        
        # Configure tag for hyperlinks
        self.results_text.tag_configure(
            "hyperlink",
            foreground="blue",
            underline=True
        )
        
        # Bind click event to hyperlinks
        self.results_text.tag_bind(
            "hyperlink",
            "<Button-1>",
            self.open_link
        )
        
        # Status info
        self.status_var = tk.StringVar(value="No links loaded yet.")
        self.status_label = ttk.Label(
            self.frame,
            textvariable=self.status_var
        )
        self.status_label.pack(padx=20, pady=5, anchor=tk.W)
        
        # Update UI state
        self.update_ui()
    
    def update_ui(self):
        """Update the UI state based on application data."""
        # Update category dropdown
        categories = ["All"] + sorted([c.name for c in self.app.categories])
        self.category_combo.config(values=categories)
        
        # Update status
        bookmark_count = len(self.app.bookmarks)
        if bookmark_count > 0:
            self.status_var.set(f"{bookmark_count} bookmarks loaded across {len(self.app.categories)} categories.")
            self.shuffle_button.config(state=tk.NORMAL)
        else:
            self.status_var.set("No links loaded yet.")
            self.shuffle_button.config(state=tk.DISABLED)
    
    def shuffle_links(self):
        """Shuffle and display random links."""
        # Get filter settings
        category = self.category_var.get()
        category = None if category == "All" else category
        
        num_links = self.num_links_var.get()
        
        rating = self.rating_var.get()
        min_rating = None if rating == "Any" else int(rating)
        
        # Filter bookmarks
        filtered_bookmarks = self.app.link_controller.filter_bookmarks(
            category=category,
            min_rating=min_rating
        )
        
        if not filtered_bookmarks:
            self.app.main_window.update_status("No bookmarks match the current filters.")
            self.clear_results()
            return
        
        # Adjust num_links if needed
        num_links = min(num_links, len(filtered_bookmarks))
        
        # Prepare tracking set for shuffle
        self.app.link_controller.shown_links = {b.url for b in self.app.link_controller.shuffled_bookmarks}
        
        # Shuffle bookmarks
        shuffled = []
        available = [b for b in filtered_bookmarks if b.url not in self.app.link_controller.shown_links]
        
        if not available:
            # All have been shown, reset tracking
            self.app.link_controller.shown_links.clear()
            available = filtered_bookmarks
        
        # Get random bookmarks
        import random
        random.shuffle(available)
        shuffled = available[:num_links]
        
        # Update tracking
        self.app.link_controller.shuffled_bookmarks = shuffled
        for bookmark in shuffled:
            self.app.link_controller.shown_links.add(bookmark.url)
        
        # Display results
        self.display_shuffled_links(shuffled)
        
        # Update status
        self.app.main_window.update_status(f"Displaying {len(shuffled)} random bookmarks.")
    
    def display_shuffled_links(self, bookmarks):
        """
        Display shuffled bookmarks in the text widget.
        
        Args:
            bookmarks: List of bookmarks to display
        """
        # Clear previous results
        self.clear_results()
        
        # Add each bookmark
        for i, bookmark in enumerate(bookmarks):
            # Add title
            self.results_text.insert(tk.END, f"{i+1}. {bookmark.title}\n", "title")
            
            # Add URL as hyperlink
            self.results_text.insert(tk.END, f"{bookmark.url}\n", "hyperlink")
            
            # Add category and rating if available
            category = bookmark.category if bookmark.category != "Uncategorized" else ""
            rating = f"Rating: {bookmark.rating}/5" if bookmark.rating else ""
            
            info = ""
            if category and rating:
                info = f"[{category} | {rating}]"
            elif category:
                info = f"[{category}]"
            elif rating:
                info = f"[{rating}]"
            
            if info:
                self.results_text.insert(tk.END, f"{info}\n")
            
            # Add separator
            self.results_text.insert(tk.END, "\n")
        
        # Make text widget read-only
        self.results_text.config(state=tk.DISABLED)
    
    def clear_results(self):
        """Clear the results text widget."""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
    
    def open_link(self, event):
        """
        Open a link when clicked.
        
        Args:
            event: The click event
        """
        # Get position of click
        index = self.results_text.index(f"@{event.x},{event.y}")
        
        # Get the hyperlink tag range at this position
        tag_ranges = self.results_text.tag_prevrange("hyperlink", index + "+1c")
        
        if tag_ranges:
            # Extract the URL
            start, end = tag_ranges
            url = self.results_text.get(start, end)
            
            # Open in browser
            if url.startswith(('http://', 'https://')):
                webbrowser.open(url)
            else:
                # Try adding https:// prefix if missing
                webbrowser.open('https://' + url)