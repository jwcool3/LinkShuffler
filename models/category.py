class Category:
    """
    Represents a category with name and associated bookmarks.
    """
    def __init__(self, name):
        """
        Initialize a category.
        
        Args:
            name (str): The name of the category
        """
        self.name = name
        self.bookmarks = []  # List of bookmarks in this category
    
    def __str__(self):
        """String representation of the category."""
        return f"{self.name} ({len(self.bookmarks)} bookmarks)"
    
    def __repr__(self):
        """Representation of the category for debugging."""
        return f"Category(name='{self.name}')"
    
    def add_bookmark(self, bookmark):
        """
        Add a bookmark to this category.
        
        Args:
            bookmark: The bookmark to add
        """
        if bookmark not in self.bookmarks:
            self.bookmarks.append(bookmark)
            bookmark.category = self.name
    
    def remove_bookmark(self, bookmark):
        """
        Remove a bookmark from this category.
        
        Args:
            bookmark: The bookmark to remove
        """
        if bookmark in self.bookmarks:
            self.bookmarks.remove(bookmark)
            if bookmark.category == self.name:
                bookmark.category = "Uncategorized"
    
    def to_dict(self):
        """Convert the category to a dictionary for serialization."""
        return {
            "name": self.name,
            "bookmarks": [bookmark.url for bookmark in self.bookmarks]
        }
    
    @classmethod
    def from_dict(cls, data, bookmarks):
        """
        Create a category from a dictionary.
        
        Args:
            data (dict): The dictionary representation of the category
            bookmarks (list): A list of all bookmarks to reference
        
        Returns:
            Category: A new Category instance
        """
        category = cls(data["name"])
        bookmark_urls = data.get("bookmarks", [])
        for bookmark in bookmarks:
            if bookmark.url in bookmark_urls:
                category.add_bookmark(bookmark)
        return category