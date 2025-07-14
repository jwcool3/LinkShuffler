# Enhanced Search, Sort, and Grouping Features for Bookmark Manager

import re
import datetime
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from difflib import SequenceMatcher
from urllib.parse import urlparse
import tkinter as tk
from tkinter import ttk
from functools import lru_cache
import threading
from concurrent.futures import ThreadPoolExecutor
import sqlite3
import os


# ===============================
# PERFORMANCE OPTIMIZATIONS
# ===============================

class PerformanceOptimizations:
    """Performance optimization utilities for bookmark management"""
    
    @staticmethod
    @lru_cache(maxsize=256)
    def cached_domain_extraction(url: str) -> str:
        """Cache domain extraction results for better performance"""
        try:
            domain = urlparse(url).netloc
            return domain.replace('www.', '').lower()
        except Exception:
            return ""
    
    @staticmethod
    @lru_cache(maxsize=128)
    def cached_url_validation(url: str) -> bool:
        """Cache URL validation results"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False


class LazyBookmarkLoader:
    """Lazy loading for large bookmark collections"""
    
    def __init__(self, bookmarks: List, page_size: int = 50):
        self.bookmarks = bookmarks
        self.page_size = page_size
        self.loaded_pages = {}
        self.total_pages = (len(bookmarks) + page_size - 1) // page_size
    
    def get_page(self, page_num: int) -> List:
        """Get a specific page of bookmarks"""
        if page_num < 0 or page_num >= self.total_pages:
            return []
        
        if page_num not in self.loaded_pages:
            start = page_num * self.page_size
            end = min(start + self.page_size, len(self.bookmarks))
            self.loaded_pages[page_num] = self.bookmarks[start:end]
        
        return self.loaded_pages[page_num]
    
    def clear_cache(self):
        """Clear the page cache"""
        self.loaded_pages.clear()


class BackgroundProcessor:
    """Background processing for expensive operations"""
    
    def __init__(self, max_workers: int = 2):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.running_tasks = {}
    
    def submit_task(self, task_id: str, func, *args, **kwargs):
        """Submit a task to run in background"""
        if task_id in self.running_tasks:
            return self.running_tasks[task_id]
        
        future = self.executor.submit(func, *args, **kwargs)
        self.running_tasks[task_id] = future
        
        # Clean up completed tasks
        def cleanup(f):
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
        
        future.add_done_callback(cleanup)
        return future
    
    def shutdown(self):
        """Shutdown the executor"""
        self.executor.shutdown(wait=True)


class SearchIndex:
    """Efficient search indexing for fast lookups"""
    
    def __init__(self):
        self.title_index = {}
        self.url_index = {}
        self.keyword_index = {}
        self.category_index = {}
        self.is_built = False
    
    def build_index(self, bookmarks: List):
        """Build search index for fast lookups"""
        self.clear_index()
        
        for bookmark in bookmarks:
            # Index title words
            title_words = self._tokenize(bookmark.title.lower())
            for word in title_words:
                if word not in self.title_index:
                    self.title_index[word] = set()
                self.title_index[word].add(bookmark)
            
            # Index URL words
            url_words = self._tokenize(bookmark.url.lower())
            for word in url_words:
                if word not in self.url_index:
                    self.url_index[word] = set()
                self.url_index[word].add(bookmark)
            
            # Index keywords
            if hasattr(bookmark, 'keywords') and bookmark.keywords:
                for keyword in bookmark.keywords:
                    keyword_words = self._tokenize(keyword.lower())
                    for word in keyword_words:
                        if word not in self.keyword_index:
                            self.keyword_index[word] = set()
                        self.keyword_index[word].add(bookmark)
            
            # Index category
            category_words = self._tokenize(bookmark.category.lower())
            for word in category_words:
                if word not in self.category_index:
                    self.category_index[word] = set()
                self.category_index[word].add(bookmark)
        
        self.is_built = True
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization with minimum word length"""
        return [word.strip() for word in re.split(r'[^\w]+', text) if len(word.strip()) > 2]
    
    def search(self, query: str, search_fields: List[str] = None) -> List:
        """Fast indexed search"""
        if not self.is_built:
            return []
        
        if search_fields is None:
            search_fields = ['title', 'url', 'keywords', 'category']
        
        query_words = self._tokenize(query.lower())
        if not query_words:
            return []
        
        results = set()
        
        for word in query_words:
            word_results = set()
            
            if 'title' in search_fields and word in self.title_index:
                word_results.update(self.title_index[word])
            
            if 'url' in search_fields and word in self.url_index:
                word_results.update(self.url_index[word])
            
            if 'keywords' in search_fields and word in self.keyword_index:
                word_results.update(self.keyword_index[word])
            
            if 'category' in search_fields and word in self.category_index:
                word_results.update(self.category_index[word])
            
            if not results:
                results = word_results
            else:
                results = results.intersection(word_results)
        
        return list(results)
    
    def clear_index(self):
        """Clear all indexes"""
        self.title_index.clear()
        self.url_index.clear()
        self.keyword_index.clear()
        self.category_index.clear()
        self.is_built = False


class DatabaseManager:
    """SQLite database for large bookmark collections"""
    
    def __init__(self, db_path: str = "bookmarks.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with indexes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                category TEXT DEFAULT 'Uncategorized',
                rating INTEGER,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                keywords TEXT,
                description TEXT
            )
        ''')
        
        # Add indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON bookmarks(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rating ON bookmarks(rating)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON bookmarks(date_added)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_title ON bookmarks(title)')
        
        conn.commit()
        conn.close()
    
    def search_bookmarks(self, query: str, limit: int = 100) -> List[Dict]:
        """Fast database search with LIKE queries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM bookmarks 
            WHERE title LIKE ? OR url LIKE ? OR keywords LIKE ?
            ORDER BY date_added DESC 
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', f'%{query}%', limit))
        
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_bookmarks_by_category(self, category: str) -> List[Dict]:
        """Get bookmarks by category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM bookmarks WHERE category = ? ORDER BY title', (category,))
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return results


# ===============================
# ORIGINAL CLASSES WITH OPTIMIZATIONS
# ===============================

class SortOrder(Enum):
    ASC = "ascending"
    DESC = "descending"


class GroupBy(Enum):
    CATEGORY = "category"
    DOMAIN = "domain"
    RATING = "rating"
    DATE_ADDED = "date_added"
    FIRST_LETTER = "first_letter"
    TAG = "tag"


@dataclass
class SearchFilter:
    """Advanced search filter configuration"""
    query: str = ""
    categories: List[str] = None
    min_rating: Optional[int] = None
    max_rating: Optional[int] = None
    domains: List[str] = None
    tags: List[str] = None
    date_from: Optional[datetime.date] = None
    date_to: Optional[datetime.date] = None
    fuzzy_threshold: float = 0.6
    case_sensitive: bool = False
    regex_enabled: bool = False

    def __post_init__(self):
        """Initialize default values for mutable fields"""
        if self.categories is None:
            self.categories = []
        if self.domains is None:
            self.domains = []
        if self.tags is None:
            self.tags = []


class EnhancedBookmarkManager:
    """Enhanced bookmark management with advanced features and performance optimizations"""
    
    def __init__(self, app):
        self.app = app
        self.search_history = []
        self.current_sort = {"field": "title", "order": SortOrder.ASC}
        self.current_group = None
        self.grouped_bookmarks = {}
        
        # Get config settings
        self.config = getattr(app, 'config', None)
        
        # Performance optimizations
        self.search_index = SearchIndex()
        self.background_processor = BackgroundProcessor(max_workers=2)
        self.lazy_loader = None
        self.db_manager = None
        
        # Performance settings from config
        self.use_indexing = self.config.use_search_indexing if self.config else True
        self.use_lazy_loading = self.config.use_lazy_loading if self.config else True
        self.lazy_loading_threshold = self.config.lazy_loading_threshold if self.config else 100
        self.use_database = self.config.use_database_mode if self.config else False
        self.background_processing = self.config.background_processing if self.config else True
        
        # Initialize search index in background if enabled
        if self.background_processing:
            self._rebuild_search_index()
        
    def _rebuild_search_index(self):
        """Rebuild search index in background"""
        if self.use_indexing and len(self.app.bookmarks) > 10:
            self.background_processor.submit_task(
                "rebuild_index",
                self.search_index.build_index,
                self.app.bookmarks
            )
    
    def enable_database_mode(self, db_path: str = "bookmarks.db"):
        """Enable database mode for very large collections"""
        self.use_database = True
        self.db_manager = DatabaseManager(db_path)
        # TODO: Sync bookmarks to database
    
    def set_lazy_loading(self, enabled: bool, threshold: int = None):
        """Configure lazy loading settings"""
        self.use_lazy_loading = enabled
        if threshold is not None:
            self.lazy_loading_threshold = threshold
        elif self.config:
            self.lazy_loading_threshold = self.config.lazy_loading_threshold
        
        if enabled and len(self.app.bookmarks) > self.lazy_loading_threshold:
            self.lazy_loader = LazyBookmarkLoader(self.app.bookmarks)
    
    # ===============================
    # ENHANCED SEARCH FUNCTIONALITY
    # ===============================
    
    def advanced_search(self, search_filter: SearchFilter) -> List:
        """
        Perform advanced search with multiple criteria and performance optimizations
        
        Args:
            search_filter: SearchFilter object with search criteria
            
        Returns:
            List of matching bookmarks
        """
        bookmarks = self.app.bookmarks.copy()
        
        # Use indexed search for text queries if available
        if (search_filter.query and 
            self.use_indexing and 
            self.search_index.is_built and
            len(bookmarks) > 50):
            
            # Fast indexed search
            indexed_results = self.search_index.search(search_filter.query)
            if indexed_results:
                bookmarks = indexed_results
        elif search_filter.query:
            # Fallback to regular text search
            bookmarks = self._text_search(bookmarks, search_filter)
        
        # Apply other filters
        bookmarks = self._apply_filters(bookmarks, search_filter)
        
        # Store search in history
        if search_filter.query:
            self._add_to_search_history(search_filter.query)
        
        return bookmarks
    
    def _apply_filters(self, bookmarks: List, search_filter: SearchFilter) -> List:
        """Apply non-text filters to bookmarks"""
        # Category filter
        if search_filter.categories:
            bookmarks = [b for b in bookmarks if b.category in search_filter.categories]
        
        # Rating filter
        if search_filter.min_rating is not None:
            bookmarks = [b for b in bookmarks 
                        if b.rating and b.rating >= search_filter.min_rating]
        
        if search_filter.max_rating is not None:
            bookmarks = [b for b in bookmarks 
                        if b.rating and b.rating <= search_filter.max_rating]
        
        # Domain filter
        if search_filter.domains:
            bookmarks = self._filter_by_domains(bookmarks, search_filter.domains)
        
        # Tag filter
        if search_filter.tags:
            bookmarks = self._filter_by_tags(bookmarks, search_filter.tags)
        
        # Date filter
        if search_filter.date_from or search_filter.date_to:
            bookmarks = self._filter_by_date(bookmarks, search_filter.date_from, search_filter.date_to)
        
        return bookmarks
    
    def _text_search(self, bookmarks: List, search_filter: SearchFilter) -> List:
        """Enhanced text search with fuzzy matching and regex support"""
        query = search_filter.query
        
        if not search_filter.case_sensitive:
            query = query.lower()
        
        results = []
        
        for bookmark in bookmarks:
            # Prepare search text
            search_text = f"{bookmark.title} {bookmark.url}"
            if hasattr(bookmark, 'description'):
                search_text += f" {bookmark.description}"
            
            # Add keywords to search text
            if hasattr(bookmark, 'keywords') and bookmark.keywords:
                search_text += f" {' '.join(bookmark.keywords)}"
            
            if not search_filter.case_sensitive:
                search_text = search_text.lower()
            
            # Regex search
            if search_filter.regex_enabled:
                try:
                    if re.search(query, search_text):
                        results.append(bookmark)
                        continue
                except re.error:
                    pass  # Fall back to normal search
            
            # Exact match
            if query in search_text:
                results.append(bookmark)
                continue
            
            # Fuzzy search
            similarity = SequenceMatcher(None, query, bookmark.title.lower()).ratio()
            if similarity >= search_filter.fuzzy_threshold:
                results.append(bookmark)
        
        return results
    
    def _filter_by_domains(self, bookmarks: List, domains: List[str]) -> List:
        """Filter bookmarks by domain using cached extraction"""
        filtered = []
        for bookmark in bookmarks:
            domain = self._get_domain(bookmark)
            if any(d in domain for d in domains):
                filtered.append(bookmark)
        return filtered
    
    def _filter_by_tags(self, bookmarks: List, tags: List[str]) -> List:
        """Filter bookmarks by tags"""
        return [b for b in bookmarks 
                if hasattr(b, 'keywords') and b.keywords and any(tag in b.keywords for tag in tags)]
    
    def _filter_by_date(self, bookmarks: List, date_from: datetime.date, date_to: datetime.date) -> List:
        """Filter bookmarks by date range"""
        filtered = []
        for bookmark in bookmarks:
            if hasattr(bookmark, 'date_added') and bookmark.date_added:
                bookmark_date = bookmark.date_added.date() if isinstance(bookmark.date_added, datetime.datetime) else bookmark.date_added
                
                if date_from and bookmark_date < date_from:
                    continue
                if date_to and bookmark_date > date_to:
                    continue
                
                filtered.append(bookmark)
        return filtered
    
    def _add_to_search_history(self, query: str):
        """Add search query to history"""
        if query not in self.search_history:
            self.search_history.insert(0, query)
            # Keep only configured number of searches
            max_history = self.config.max_search_history if self.config else 20
            self.search_history = self.search_history[:max_history]
    
    def get_search_suggestions(self, partial_query: str) -> List[str]:
        """Get search suggestions based on history and bookmark content"""
        suggestions = []
        
        # From search history
        for query in self.search_history:
            if partial_query.lower() in query.lower():
                suggestions.append(query)
        
        # From bookmark titles (optimized)
        if self.search_index.is_built:
            # Use index for faster suggestions
            words = self.search_index._tokenize(partial_query.lower())
            for word in words:
                if word in self.search_index.title_index:
                    for bookmark in list(self.search_index.title_index[word])[:5]:  # Limit results
                        title_words = bookmark.title.split()
                        for title_word in title_words:
                            if (len(title_word) > 3 and 
                                partial_query.lower() in title_word.lower() and 
                                title_word not in suggestions):
                                suggestions.append(title_word)
        else:
            # Fallback to linear search
            for bookmark in self.app.bookmarks[:50]:  # Limit for performance
                words = bookmark.title.split()
                for word in words:
                    if (len(word) > 3 and 
                        partial_query.lower() in word.lower() and 
                        word not in suggestions):
                        suggestions.append(word)
        
        return suggestions[:10]  # Limit to 10 suggestions
    
    # ===============================
    # ENHANCED SORTING FUNCTIONALITY
    # ===============================
    
    def sort_bookmarks(self, bookmarks: List, field: str, order: SortOrder = SortOrder.ASC) -> List:
        """
        Sort bookmarks by various criteria with performance optimizations
        
        Args:
            bookmarks: List of bookmarks to sort
            field: Field to sort by ('title', 'url', 'category', 'rating', 'date_added', 'domain', 'length')
            order: Sort order (ASC or DESC)
            
        Returns:
            Sorted list of bookmarks
        """
        reverse = (order == SortOrder.DESC)
        
        # Use cached domain extraction for domain sorting
        if field == "domain":
            return sorted(bookmarks, key=self._get_domain, reverse=reverse)
        
        # For large collections, consider using background sorting
        if len(bookmarks) > 1000:
            return self._background_sort(bookmarks, field, reverse)
        
        # Regular sorting
        if field == "title":
            return sorted(bookmarks, key=lambda x: x.title.lower(), reverse=reverse)
        
        elif field == "url":
            return sorted(bookmarks, key=lambda x: x.url.lower(), reverse=reverse)
        
        elif field == "category":
            return sorted(bookmarks, key=lambda x: x.category.lower(), reverse=reverse)
        
        elif field == "rating":
            return sorted(bookmarks, key=lambda x: x.rating or 0, reverse=reverse)
        
        elif field == "date_added":
            return sorted(bookmarks, 
                         key=lambda x: x.date_added if hasattr(x, 'date_added') and x.date_added else datetime.datetime.min,
                         reverse=reverse)
        
        elif field == "length":
            return sorted(bookmarks, key=lambda x: len(x.title), reverse=reverse)
        
        elif field == "popularity":
            # Sort by visit count if available
            return sorted(bookmarks, 
                         key=lambda x: getattr(x, 'visit_count', 0), 
                         reverse=reverse)
        
        elif field == "smart":
            # Smart sort combining multiple factors
            return self._smart_sort(bookmarks, reverse)
        
        else:
            return bookmarks
    
    def _background_sort(self, bookmarks: List, field: str, reverse: bool) -> List:
        """Sort large collections in background"""
        # For now, just use regular sorting
        # In a real implementation, this would use the background processor
        return sorted(bookmarks, key=lambda x: getattr(x, field, ""), reverse=reverse)
    
    def _get_domain(self, bookmark) -> str:
        """Extract domain from bookmark URL using cached extraction"""
        return PerformanceOptimizations.cached_domain_extraction(bookmark.url)
    
    def _smart_sort(self, bookmarks: List, reverse: bool = False) -> List:
        """Smart sorting algorithm combining multiple factors"""
        def smart_score(bookmark):
            score = 0
            
            # Rating weight (40%)
            if bookmark.rating:
                score += bookmark.rating * 0.4
            
            # Visit count weight (30%)
            if hasattr(bookmark, 'visit_count'):
                score += (bookmark.visit_count or 0) * 0.3
            
            # Recency weight (20%)
            if hasattr(bookmark, 'date_added') and bookmark.date_added:
                days_old = (datetime.datetime.now() - bookmark.date_added).days
                recency_score = max(0, 365 - days_old) / 365  # Normalize to 0-1
                score += recency_score * 0.2
            
            # Title length weight (10%) - shorter titles often more focused
            title_score = max(0, 100 - len(bookmark.title)) / 100
            score += title_score * 0.1
            
            return score
        
        return sorted(bookmarks, key=smart_score, reverse=not reverse)
    
    def multi_sort(self, bookmarks: List, sort_criteria: List[Tuple[str, SortOrder]]) -> List:
        """Sort by multiple criteria in order of priority"""
        sorted_bookmarks = bookmarks.copy()
        
        # Apply sorts in reverse order (last criteria first)
        for field, order in reversed(sort_criteria):
            sorted_bookmarks = self.sort_bookmarks(sorted_bookmarks, field, order)
        
        return sorted_bookmarks
    
    # ===============================
    # GROUPING FUNCTIONALITY
    # ===============================
    
    def group_bookmarks(self, bookmarks: List, group_by: GroupBy) -> Dict[str, List]:
        """
        Group bookmarks by various criteria with performance optimizations
        
        Args:
            bookmarks: List of bookmarks to group
            group_by: Grouping criteria
            
        Returns:
            Dictionary with group names as keys and bookmark lists as values
        """
        groups = {}
        
        # For large collections, use background processing if enabled
        if len(bookmarks) > 500 and self.background_processing:
            return self._background_group(bookmarks, group_by)
        
        for bookmark in bookmarks:
            group_key = self._get_group_key(bookmark, group_by)
            
            if group_key not in groups:
                groups[group_key] = []
            
            groups[group_key].append(bookmark)
        
        # Sort groups by key
        return dict(sorted(groups.items()))
    
    def _background_group(self, bookmarks: List, group_by: GroupBy) -> Dict[str, List]:
        """Group large collections in background"""
        # For now, just use regular grouping
        # In a real implementation, this would use the background processor
        groups = {}
        for bookmark in bookmarks:
            group_key = self._get_group_key(bookmark, group_by)
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(bookmark)
        return dict(sorted(groups.items()))
    
    def _get_group_key(self, bookmark, group_by: GroupBy) -> str:
        """Get the group key for a bookmark based on grouping criteria"""
        
        if group_by == GroupBy.CATEGORY:
            return bookmark.category
        
        elif group_by == GroupBy.DOMAIN:
            return self._get_domain(bookmark) or "Unknown"
        
        elif group_by == GroupBy.RATING:
            if bookmark.rating:
                return f"{bookmark.rating} Star{'s' if bookmark.rating != 1 else ''}"
            return "Unrated"
        
        elif group_by == GroupBy.DATE_ADDED:
            if hasattr(bookmark, 'date_added') and bookmark.date_added:
                return bookmark.date_added.strftime("%Y-%m")
            return "Unknown Date"
        
        elif group_by == GroupBy.FIRST_LETTER:
            return bookmark.title[0].upper() if bookmark.title else "#"
        
        elif group_by == GroupBy.TAG:
            if hasattr(bookmark, 'keywords') and bookmark.keywords:
                return bookmark.keywords[0]  # Use first keyword
            return "Untagged"
        
        else:
            return "Default"
    
    def get_group_statistics(self, groups: Dict[str, List]) -> Dict[str, Dict]:
        """Get statistics for each group"""
        stats = {}
        
        for group_name, bookmarks in groups.items():
            stats[group_name] = {
                'count': len(bookmarks),
                'avg_rating': self._calculate_avg_rating(bookmarks),
                'most_common_domain': self._get_most_common_domain(bookmarks),
                'newest': max(bookmarks, key=lambda x: getattr(x, 'date_added', datetime.datetime.min)),
                'oldest': min(bookmarks, key=lambda x: getattr(x, 'date_added', datetime.datetime.max))
            }
        
        return stats
    
    def _calculate_avg_rating(self, bookmarks: List) -> float:
        """Calculate average rating for a list of bookmarks"""
        rated_bookmarks = [b for b in bookmarks if b.rating]
        if not rated_bookmarks:
            return 0.0
        return sum(b.rating for b in rated_bookmarks) / len(rated_bookmarks)
    
    def _get_most_common_domain(self, bookmarks: List) -> str:
        """Get the most common domain in a list of bookmarks"""
        domain_counts = {}
        
        for bookmark in bookmarks:
            domain = self._get_domain(bookmark)
            if domain:
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        if not domain_counts:
            return "Unknown"
        
        return max(domain_counts.items(), key=lambda x: x[1])[0]
    
    # ===============================
    # PERFORMANCE MANAGEMENT
    # ===============================
    
    def refresh_indexes(self):
        """Refresh search indexes when bookmarks change"""
        if self.use_indexing:
            self._rebuild_search_index()
        
        if self.use_lazy_loading and len(self.app.bookmarks) > self.lazy_loading_threshold:
            self.lazy_loader = LazyBookmarkLoader(self.app.bookmarks)
    
    def cleanup(self):
        """Clean up background processes"""
        if self.background_processor:
            self.background_processor.shutdown()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            'total_bookmarks': len(self.app.bookmarks),
            'search_index_built': self.search_index.is_built,
            'using_lazy_loading': self.use_lazy_loading and self.lazy_loader is not None,
            'using_database': self.use_database,
            'search_history_size': len(self.search_history),
            'background_tasks': len(self.background_processor.running_tasks) if self.background_processor else 0
        }


# ===============================
# ENHANCED UI COMPONENTS
# ===============================

class AdvancedSearchDialog:
    """Advanced search dialog with multiple filters"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Advanced Search")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.geometry("500x600")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame with scrollbar
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Search query
        ttk.Label(main_frame, text="Search Query:").pack(anchor=tk.W)
        self.query_var = tk.StringVar()
        query_frame = ttk.Frame(main_frame)
        query_frame.pack(fill=tk.X, pady=5)
        
        self.query_entry = ttk.Entry(query_frame, textvariable=self.query_var, width=40)
        self.query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Search options
        options_frame = ttk.LabelFrame(main_frame, text="Search Options")
        options_frame.pack(fill=tk.X, pady=10)
        
        self.case_sensitive_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Case sensitive", 
                       variable=self.case_sensitive_var).pack(anchor=tk.W)
        
        self.regex_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Enable regex", 
                       variable=self.regex_var).pack(anchor=tk.W)
        
        # Fuzzy threshold
        fuzzy_frame = ttk.Frame(options_frame)
        fuzzy_frame.pack(fill=tk.X, pady=5)
        ttk.Label(fuzzy_frame, text="Fuzzy match threshold:").pack(side=tk.LEFT)
        self.fuzzy_var = tk.DoubleVar(value=0.6)
        ttk.Scale(fuzzy_frame, from_=0.1, to=1.0, variable=self.fuzzy_var, 
                 orient=tk.HORIZONTAL).pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # Category filter
        category_frame = ttk.LabelFrame(main_frame, text="Categories")
        category_frame.pack(fill=tk.X, pady=10)
        
        self.category_vars = {}
        for category in sorted([c.name for c in self.app.categories]):
            var = tk.BooleanVar()
            self.category_vars[category] = var
            ttk.Checkbutton(category_frame, text=category, variable=var).pack(anchor=tk.W)
        
        # Rating filter
        rating_frame = ttk.LabelFrame(main_frame, text="Rating")
        rating_frame.pack(fill=tk.X, pady=10)
        
        rating_controls = ttk.Frame(rating_frame)
        rating_controls.pack(fill=tk.X)
        
        ttk.Label(rating_controls, text="Min:").pack(side=tk.LEFT)
        self.min_rating_var = tk.StringVar(value="")
        ttk.Combobox(rating_controls, textvariable=self.min_rating_var, 
                    values=["", "1", "2", "3", "4", "5"], width=5).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(rating_controls, text="Max:").pack(side=tk.LEFT, padx=(10, 0))
        self.max_rating_var = tk.StringVar(value="")
        ttk.Combobox(rating_controls, textvariable=self.max_rating_var, 
                    values=["", "1", "2", "3", "4", "5"], width=5).pack(side=tk.LEFT, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="Search", command=self.search).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset", command=self.reset).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT, padx=5)
    
    def search(self):
        """Perform the search and close dialog"""
        # Build search filter
        search_filter = SearchFilter(
            query=self.query_var.get(),
            case_sensitive=self.case_sensitive_var.get(),
            regex_enabled=self.regex_var.get(),
            fuzzy_threshold=self.fuzzy_var.get()
        )
        
        # Get selected categories
        selected_categories = [cat for cat, var in self.category_vars.items() if var.get()]
        if selected_categories:
            search_filter.categories = selected_categories
        
        # Get rating range
        if self.min_rating_var.get():
            search_filter.min_rating = int(self.min_rating_var.get())
        if self.max_rating_var.get():
            search_filter.max_rating = int(self.max_rating_var.get())
        
        self.result = search_filter
        self.dialog.destroy()
    
    def reset(self):
        """Reset all filters"""
        self.query_var.set("")
        self.case_sensitive_var.set(False)
        self.regex_var.set(False)
        self.fuzzy_var.set(0.6)
        
        for var in self.category_vars.values():
            var.set(False)
        
        self.min_rating_var.set("")
        self.max_rating_var.set("")
    
    def cancel(self):
        """Cancel the dialog"""
        self.result = None
        self.dialog.destroy()


class SortConfigDialog:
    """Dialog for configuring multi-criteria sorting"""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Sort Configuration")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.geometry("400x300")
        
        self.sort_criteria = []
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Instructions
        ttk.Label(main_frame, text="Configure sorting criteria (top = highest priority):").pack(anchor=tk.W)
        
        # Sort criteria list
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.criteria_listbox = tk.Listbox(list_frame)
        self.criteria_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, command=self.criteria_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.criteria_listbox.config(yscrollcommand=scrollbar.set)
        
        # Controls
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=5)
        
        # Add criteria
        add_frame = ttk.Frame(controls_frame)
        add_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(add_frame, text="Field:").pack(side=tk.LEFT)
        self.field_var = tk.StringVar()
        field_combo = ttk.Combobox(add_frame, textvariable=self.field_var,
                                  values=["title", "url", "category", "rating", "date_added", "domain", "smart"],
                                  state="readonly", width=15)
        field_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(add_frame, text="Order:").pack(side=tk.LEFT, padx=(10, 0))
        self.order_var = tk.StringVar(value="ascending")
        order_combo = ttk.Combobox(add_frame, textvariable=self.order_var,
                                  values=["ascending", "descending"],
                                  state="readonly", width=10)
        order_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(add_frame, text="Add", command=self.add_criteria).pack(side=tk.LEFT, padx=5)
        
        # List controls
        list_controls = ttk.Frame(controls_frame)
        list_controls.pack(fill=tk.X, pady=5)
        
        ttk.Button(list_controls, text="Remove", command=self.remove_criteria).pack(side=tk.LEFT, padx=5)
        ttk.Button(list_controls, text="Move Up", command=self.move_up).pack(side=tk.LEFT, padx=5)
        ttk.Button(list_controls, text="Move Down", command=self.move_down).pack(side=tk.LEFT, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="Apply", command=self.apply).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT, padx=5)
    
    def add_criteria(self):
        """Add sort criteria to the list"""
        field = self.field_var.get()
        order = self.order_var.get()
        
        if field:
            criteria = (field, SortOrder.ASC if order == "ascending" else SortOrder.DESC)
            self.sort_criteria.append(criteria)
            self.criteria_listbox.insert(tk.END, f"{field} ({order})")
    
    def remove_criteria(self):
        """Remove selected criteria"""
        selection = self.criteria_listbox.curselection()
        if selection:
            index = selection[0]
            self.criteria_listbox.delete(index)
            del self.sort_criteria[index]
    
    def move_up(self):
        """Move selected criteria up"""
        selection = self.criteria_listbox.curselection()
        if selection and selection[0] > 0:
            index = selection[0]
            # Swap in list
            self.sort_criteria[index], self.sort_criteria[index-1] = \
                self.sort_criteria[index-1], self.sort_criteria[index]
            
            # Update listbox
            item = self.criteria_listbox.get(index)
            self.criteria_listbox.delete(index)
            self.criteria_listbox.insert(index-1, item)
            self.criteria_listbox.selection_set(index-1)
    
    def move_down(self):
        """Move selected criteria down"""
        selection = self.criteria_listbox.curselection()
        if selection and selection[0] < len(self.sort_criteria) - 1:
            index = selection[0]
            # Swap in list
            self.sort_criteria[index], self.sort_criteria[index+1] = \
                self.sort_criteria[index+1], self.sort_criteria[index]
            
            # Update listbox
            item = self.criteria_listbox.get(index)
            self.criteria_listbox.delete(index)
            self.criteria_listbox.insert(index+1, item)
            self.criteria_listbox.selection_set(index+1)
    
    def apply(self):
        """Apply the sort configuration"""
        self.result = self.sort_criteria.copy()
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel the dialog"""
        self.result = None
        self.dialog.destroy() 