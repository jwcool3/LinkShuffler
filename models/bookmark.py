from datetime import datetime

class Bookmark:
    """
    Represents a bookmark with URL, title, category, and rating.
    """
    def __init__(self, url, title, category="Uncategorized", rating=None):
        """
        Initialize a bookmark.
        
        Args:
            url (str): The URL of the bookmark
            title (str): The title of the bookmark
            category (str, optional): The category of the bookmark. Defaults to "Uncategorized".
            rating (int, optional): The rating of the bookmark (1-5). Defaults to None.
        """
        self.url = url
        self.title = title
        self.category = category
        self.rating = rating
        self.keywords = []  # Keywords extracted from the title
        self.date_added = datetime.now()  # Add date when bookmark is created
    
    def __str__(self):
        """String representation of the bookmark."""
        return f"{self.title} ({self.url})"
    
    def __repr__(self):
        """Representation of the bookmark for debugging."""
        return f"Bookmark(url='{self.url}', title='{self.title}', category='{self.category}', rating={self.rating})"
    
    def to_dict(self):
        """Convert the bookmark to a dictionary for serialization."""
        return {
            "url": self.url,
            "title": self.title,
            "category": self.category,
            "rating": self.rating,
            "keywords": self.keywords,
            "date_added": self.date_added.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a bookmark from a dictionary."""
        bookmark = cls(
            url=data["url"],
            title=data["title"],
            category=data.get("category", "Uncategorized"),
            rating=data.get("rating")
        )
        bookmark.keywords = data.get("keywords", [])
        
        # Handle date_added field
        if "date_added" in data:
            try:
                bookmark.date_added = datetime.fromisoformat(data["date_added"])
            except (ValueError, TypeError):
                bookmark.date_added = datetime.now()
        else:
            bookmark.date_added = datetime.now()
            
        return bookmark