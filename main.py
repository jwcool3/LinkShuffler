import tkinter as tk
from app import BookmarkShufflerApp

def main():
    """
    Main entry point for the BookmarkShuffler application.
    """
    # Create root window
    root = tk.Tk()
    root.title("Bookmark Manager")
    
    # Set minimum window size
    root.minsize(800, 600)
    
    # Create app
    app = BookmarkShufflerApp(root)
    
    # Run app
    app.run()

if __name__ == "__main__":
    main()