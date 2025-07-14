# Updated models/__init__.py to include enhanced bookmark

from .category import Category
from .enhanced_bookmark import EnhancedBookmark, AdultVideoMetadata, migrate_old_bookmark_to_enhanced

# Backward compatibility
Bookmark = EnhancedBookmark

__all__ = ['Bookmark', 'EnhancedBookmark', 'Category', 'AdultVideoMetadata', 'migrate_old_bookmark_to_enhanced']