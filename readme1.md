# Bookmark Manager

A modern application for managing, categorizing, and discovering your bookmarks.

## Features

- **Load Bookmarks**: Import bookmarks from HTML files exported from browsers
- **Categorize**: Automatically categorize bookmarks based on keywords or manually
- **Shuffle**: Discover forgotten bookmarks through random shuffling
- **Search & Filter**: Find bookmarks with powerful search and filtering options
- **Organize**: Manage bookmarks with intuitive category-based organization
- **Rate**: Rate your bookmarks to prioritize important ones

## Requirements

- Python 3.6+
- Tkinter (included with most Python installations)
- scikit-learn (optional, for keyword extraction)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/bookmark-manager.git
   cd bookmark-manager
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```
python main.py
```

### Importing Bookmarks

1. Click "Load Bookmarks File" or select File → Load HTML Bookmarks
2. Select an HTML bookmarks file exported from your browser

### Managing Bookmarks

- Use the "Manage Links" tab to view, search, edit, and delete bookmarks
- Sort bookmarks by clicking on column headers
- Filter by category or rating

### Organizing Bookmarks

- Use the "Categories" tab to create, rename, and delete categories
- Move bookmarks between categories
- View bookmarks by category

### Discovering Bookmarks

- Use the "Home" tab to shuffle random bookmarks
- Filter shuffled bookmarks by category or rating
- Click on bookmark links to open them in your browser

## Project Structure

```
bookmark-manager/
├── main.py                    # Entry point
├── app.py                     # Main application class
├── models/                    # Data models
│   ├── bookmark.py            # Bookmark model
│   └── category.py            # Category model
├── controllers/               # Business logic
│   ├── file_controller.py     # File operations
│   ├── link_controller.py     # Link operations
│   └── keyword_controller.py  # Keyword detection
├── views/                     # UI components
│   ├── main_window.py         # Main window
│   ├── home_tab.py            # Home tab view
│   ├── manage_tab.py          # Manage links tab view
│   └── categories_tab.py      # Categories tab view
└── utils/                     # Utilities
    └── constants.py           # Constants and configuration
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to [scikit-learn](https://scikit-learn.org/) for text processing functionality
- Inspired by the need to manage thousands of bookmarks efficiently
