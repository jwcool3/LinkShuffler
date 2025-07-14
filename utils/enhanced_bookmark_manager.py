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
    """Enhanced bookmark management with advanced features"""
    
    def __init__(self, app):
        self.app = app
        self.search_history = []
        self.current_sort = {"field": "title", "order": SortOrder.ASC}
        self.current_group = None
        self.grouped_bookmarks = {}
        
    # ===============================
    # ENHANCED SEARCH FUNCTIONALITY
    # ===============================
    
    def advanced_search(self, search_filter: SearchFilter) -> List:
        """
        Perform advanced search with multiple criteria
        
        Args:
            search_filter: SearchFilter object with search criteria
            
        Returns:
            List of matching bookmarks
        """
        bookmarks = self.app.bookmarks.copy()
        
        # Text search
        if search_filter.query:
            bookmarks = self._text_search(bookmarks, search_filter)
        
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
        
        # Store search in history
        if search_filter.query:
            self._add_to_search_history(search_filter.query)
        
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
        """Filter bookmarks by domain"""
        filtered = []
        for bookmark in bookmarks:
            try:
                domain = urlparse(bookmark.url).netloc
                domain = domain.replace('www.', '')
                if any(d in domain for d in domains):
                    filtered.append(bookmark)
            except Exception:
                continue
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
            # Keep only last 20 searches
            self.search_history = self.search_history[:20]
    
    def get_search_suggestions(self, partial_query: str) -> List[str]:
        """Get search suggestions based on history and bookmark content"""
        suggestions = []
        
        # From search history
        for query in self.search_history:
            if partial_query.lower() in query.lower():
                suggestions.append(query)
        
        # From bookmark titles
        for bookmark in self.app.bookmarks:
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
        Sort bookmarks by various criteria
        
        Args:
            bookmarks: List of bookmarks to sort
            field: Field to sort by ('title', 'url', 'category', 'rating', 'date_added', 'domain', 'length')
            order: Sort order (ASC or DESC)
            
        Returns:
            Sorted list of bookmarks
        """
        reverse = (order == SortOrder.DESC)
        
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
        
        elif field == "domain":
            return sorted(bookmarks, key=self._get_domain, reverse=reverse)
        
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
    
    def _get_domain(self, bookmark) -> str:
        """Extract domain from bookmark URL"""
        try:
            domain = urlparse(bookmark.url).netloc
            return domain.replace('www.', '').lower()
        except Exception:
            return ""
    
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
        Group bookmarks by various criteria
        
        Args:
            bookmarks: List of bookmarks to group
            group_by: Grouping criteria
            
        Returns:
            Dictionary with group names as keys and bookmark lists as values
        """
        groups = {}
        
        for bookmark in bookmarks:
            group_key = self._get_group_key(bookmark, group_by)
            
            if group_key not in groups:
                groups[group_key] = []
            
            groups[group_key].append(bookmark)
        
        # Sort groups by key
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