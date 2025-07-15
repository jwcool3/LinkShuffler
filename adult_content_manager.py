import re
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from urllib.parse import urlparse
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import json

# ==========================================
# ENHANCED DATA STRUCTURES FOR ADULT CONTENT
# ==========================================

@dataclass
class AdultVideoMetadata:
    """Comprehensive metadata for adult video content"""
    performers: List[str] = field(default_factory=list)
    studio: Optional[str] = None
    duration: Optional[str] = None  # "MM:SS" or "HH:MM:SS"
    resolution: Optional[str] = None  # "1080p", "720p", "4K"
    file_size: Optional[str] = None
    content_tags: List[str] = field(default_factory=list)
    favorite_scenes: List[Dict[str, Any]] = field(default_factory=list)
    is_favorite: bool = False
    personal_rating: Optional[int] = None  # 1-10 scale
    personal_notes: str = ""
    
    # Content classification
    genre: Optional[str] = None
    subgenres: List[str] = field(default_factory=list)
    content_type: str = "video"  # video, image_set, etc.
    
    def to_dict(self):
        return {
            'performers': self.performers,
            'studio': self.studio,
            'duration': self.duration,
            'resolution': self.resolution,
            'file_size': self.file_size,
            'content_tags': self.content_tags,
            'favorite_scenes': self.favorite_scenes,
            'is_favorite': self.is_favorite,
            'personal_rating': self.personal_rating,
            'personal_notes': self.personal_notes,
            'genre': self.genre,
            'subgenres': self.subgenres,
            'content_type': self.content_type
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            performers=data.get('performers', []),
            studio=data.get('studio'),
            duration=data.get('duration'),
            resolution=data.get('resolution'),
            file_size=data.get('file_size'),
            content_tags=data.get('content_tags', []),
            favorite_scenes=data.get('favorite_scenes', []),
            is_favorite=data.get('is_favorite', False),
            personal_rating=data.get('personal_rating'),
            personal_notes=data.get('personal_notes', ''),
            genre=data.get('genre'),
            subgenres=data.get('subgenres', []),
            content_type=data.get('content_type', 'video')
        )


class AdultBookmark:
    """Enhanced bookmark specifically for adult content management"""
    
    def __init__(self, url, title, category="Uncategorized"):
        # Basic properties
        self.url = url
        self.title = title
        self.category = category
        
        # Enhanced properties
        self.date_added = datetime.now()
        self.date_modified = datetime.now()
        
        # Adult content metadata
        self.adult_metadata = AdultVideoMetadata()
        
        # Viewing analytics
        self.view_count = 0
        self.last_viewed = None
        self.view_history = []
        self.total_watch_time = 0  # seconds
        self.completion_rate = 0.0  # 0-1
        
        # Collections and organization
        self.collections = []  # Custom collections this belongs to
        self.is_archived = False
        self.priority = "normal"  # "high", "normal", "low"
        
        # Platform detection
        self.platform = self._detect_platform()
        self.platform_id = self._extract_platform_id()
        
        # Quality tracking
        self.link_status = "unknown"  # "working", "dead", "unknown"
        self.last_checked = None
    
    def _detect_platform(self):
        """Detect adult platform from URL"""
        if not self.url:
            return 'unknown'
            
        domain = urlparse(self.url).netloc.lower()
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Major adult platforms
        platforms = {
            'pornhub.com': 'pornhub',
            'xvideos.com': 'xvideos',
            'xhamster.com': 'xhamster',
            'redtube.com': 'redtube',
            'youporn.com': 'youporn',
            'tube8.com': 'tube8',
            'spankbang.com': 'spankbang',
            'eporner.com': 'eporner',
            'xnxx.com': 'xnxx',
            'tnaflix.com': 'tnaflix',
            'beeg.com': 'beeg',
            'txxx.com': 'txxx',
            'thumbzilla.com': 'thumbzilla',
            'porntrex.com': 'porntrex'
        }
        
        for platform_domain, platform_name in platforms.items():
            if platform_domain in domain:
                return platform_name
        
        return 'other'
    
    def _extract_platform_id(self):
        """Extract platform-specific video ID"""
        if not self.url:
            return None
            
        platform = self.platform
        
        # Platform-specific ID extraction
        if platform == 'pornhub':
            match = re.search(r'viewkey=([a-zA-Z0-9]+)', self.url)
            return match.group(1) if match else None
        elif platform == 'xvideos':
            match = re.search(r'/video(\d+)/', self.url)
            return match.group(1) if match else None
        elif platform == 'xhamster':
            match = re.search(r'/videos/[^-]+-(\d+)', self.url)
            return match.group(1) if match else None
        
        return None
    
    def add_view_session(self, duration_watched=None, completion_rate=None):
        """Record a viewing session"""
        self.view_count += 1
        self.last_viewed = datetime.now()
        
        session = {
            'timestamp': datetime.now().isoformat(),
            'duration_watched': duration_watched,
            'completion_rate': completion_rate
        }
        self.view_history.append(session)
        
        if duration_watched:
            self.total_watch_time += duration_watched
        if completion_rate:
            # Update average completion rate
            if self.completion_rate == 0:
                self.completion_rate = completion_rate
            else:
                self.completion_rate = (self.completion_rate + completion_rate) / 2
    
    def add_to_collection(self, collection_name):
        """Add to a collection"""
        if collection_name not in self.collections:
            self.collections.append(collection_name)
            self.date_modified = datetime.now()
    
    def get_viewing_frequency(self, days=30):
        """Calculate viewing frequency over specified period"""
        if not self.view_history:
            return 0
        
        cutoff = datetime.now() - timedelta(days=days)
        recent_views = [
            v for v in self.view_history
            if datetime.fromisoformat(v['timestamp']) > cutoff
        ]
        
        return len(recent_views) / days if days > 0 else 0
    
    def to_dict(self):
        """Serialize to dictionary"""
        return {
            'url': self.url,
            'title': self.title,
            'category': self.category,
            'date_added': self.date_added.isoformat(),
            'date_modified': self.date_modified.isoformat(),
            'adult_metadata': self.adult_metadata.to_dict(),
            'view_count': self.view_count,
            'last_viewed': self.last_viewed.isoformat() if self.last_viewed else None,
            'view_history': self.view_history,
            'total_watch_time': self.total_watch_time,
            'completion_rate': self.completion_rate,
            'collections': self.collections,
            'is_archived': self.is_archived,
            'priority': self.priority,
            'platform': self.platform,
            'platform_id': self.platform_id,
            'link_status': self.link_status,
            'last_checked': self.last_checked.isoformat() if self.last_checked else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """Deserialize from dictionary"""
        bookmark = cls(
            url=data['url'],
            title=data['title'],
            category=data.get('category', 'Uncategorized')
        )
        
        # Restore dates
        bookmark.date_added = datetime.fromisoformat(data['date_added'])
        bookmark.date_modified = datetime.fromisoformat(data['date_modified'])
        if data.get('last_viewed'):
            bookmark.last_viewed = datetime.fromisoformat(data['last_viewed'])
        if data.get('last_checked'):
            bookmark.last_checked = datetime.fromisoformat(data['last_checked'])
        
        # Restore metadata
        bookmark.adult_metadata = AdultVideoMetadata.from_dict(data.get('adult_metadata', {}))
        
        # Restore analytics
        bookmark.view_count = data.get('view_count', 0)
        bookmark.view_history = data.get('view_history', [])
        bookmark.total_watch_time = data.get('total_watch_time', 0)
        bookmark.completion_rate = data.get('completion_rate', 0.0)
        
        # Restore organization
        bookmark.collections = data.get('collections', [])
        bookmark.is_archived = data.get('is_archived', False)
        bookmark.priority = data.get('priority', 'normal')
        
        # Restore platform info
        bookmark.platform = data.get('platform', bookmark._detect_platform())
        bookmark.platform_id = data.get('platform_id')
        bookmark.link_status = data.get('link_status', 'unknown')
        
        return bookmark


# ==========================================
# INTELLIGENT AUTO-CATEGORIZATION ENGINE
# ==========================================

class AdultContentCategorizationEngine:
    """Specialized categorization engine for adult content"""
    
    def __init__(self, app):
        self.app = app
        
        # Predefined category patterns for adult content
        self.category_patterns = {
            'Favorites': {
                'keywords': ['favorite', 'best', 'top', 'amazing', 'perfect', 'incredible'],
                'auto_create': False  # User manually assigns favorites
            },
            'Amateur': {
                'keywords': ['amateur', 'homemade', 'real', 'couple', 'girlfriend', 'wife'],
                'domains': ['amateur.tv', 'reallifecam.com']
            },
            'Professional': {
                'keywords': ['professional', 'studio', 'production', 'hd', '4k'],
                'studios': True  # Will be populated dynamically
            },
            'Solo': {
                'keywords': ['solo', 'masturbation', 'webcam', 'cam', 'masturbating']
            },
            'Couples': {
                'keywords': ['couple', 'couples', 'boyfriend', 'girlfriend', 'husband', 'wife']
            },
            'Group': {
                'keywords': ['threesome', 'group', 'orgy', 'gangbang', 'multiple']
            },
            'Vintage': {
                'keywords': ['vintage', 'retro', 'classic', '80s', '90s', 'old']
            },
            'High Quality': {
                'keywords': ['4k', 'uhd', 'hd', '1080p', 'high quality', 'premium']
            },
            'Quick': {
                'keywords': ['quickie', 'short', 'quick', 'brief'],
                'duration_max': 600  # 10 minutes
            },
            'Long Form': {
                'keywords': ['full', 'complete', 'long', 'extended'],
                'duration_min': 1800  # 30 minutes
            }
        }
        
        # Common performer name patterns for auto-detection
        self.performer_indicators = [
            'featuring', 'with', 'starring', 'stars', '&', 'and', 'x', 'vs'
        ]
    
    def analyze_bookmarks(self):
        """Comprehensive analysis for adult content categorization"""
        if not self.app.bookmarks:
            return []
        
        suggestions = []
        
        # Method 1: Performer-based categorization
        suggestions.extend(self._analyze_by_performers())
        
        # Method 2: Studio-based categorization  
        suggestions.extend(self._analyze_by_studios())
        
        # Method 3: Platform-based categorization
        suggestions.extend(self._analyze_by_platforms())
        
        # Method 4: Content type categorization
        suggestions.extend(self._analyze_by_content_type())
        
        # Method 5: Quality-based categorization
        suggestions.extend(self._analyze_by_quality())
        
        # Method 6: Duration-based categorization
        suggestions.extend(self._analyze_by_duration())
        
        # Method 7: Viewing behavior categorization
        suggestions.extend(self._analyze_by_viewing_behavior())
        
        # Combine and rank suggestions
        return self._rank_suggestions(suggestions)
    
    def _analyze_by_performers(self):
        """Group by performers - most important for adult content"""
        performer_groups = defaultdict(list)
        
        for bookmark in self.app.bookmarks:
            if bookmark.category != "Uncategorized":
                continue
            
            # Extract performer names from title
            performers = self._extract_performers(bookmark.title)
            
            for performer in performers:
                performer_groups[performer].append(bookmark)
        
        suggestions = []
        for performer, bookmarks in performer_groups.items():
            if len(bookmarks) >= 3:  # Only suggest if 3+ videos
                confidence = min(0.95, len(bookmarks) / 5)  # High confidence for performers
                suggestions.append({
                    'category': f"{performer}",
                    'bookmarks': bookmarks,
                    'confidence': confidence,
                    'method': 'performer',
                    'description': f"Videos featuring {performer} ({len(bookmarks)} videos)",
                    'auto_apply': len(bookmarks) >= 5  # Auto-apply if 5+ videos
                })
        
        return suggestions
    
    def _analyze_by_studios(self):
        """Group by production studios"""
        studio_groups = defaultdict(list)
        
        for bookmark in self.app.bookmarks:
            if bookmark.category != "Uncategorized":
                continue
            
            studio = self._extract_studio(bookmark.title, bookmark.url)
            if studio:
                studio_groups[studio].append(bookmark)
        
        suggestions = []
        for studio, bookmarks in studio_groups.items():
            if len(bookmarks) >= 4:  # Studios need more videos to be meaningful
                confidence = min(0.85, len(bookmarks) / 8)
                suggestions.append({
                    'category': f"Studio: {studio}",
                    'bookmarks': bookmarks,
                    'confidence': confidence,
                    'method': 'studio',
                    'description': f"Content from {studio} ({len(bookmarks)} videos)"
                })
        
        return suggestions
    
    def _analyze_by_platforms(self):
        """Group by platforms with meaningful distinctions"""
        platform_groups = defaultdict(list)
        
        for bookmark in self.app.bookmarks:
            if bookmark.category != "Uncategorized":
                continue
            
            platform = bookmark.platform
            if platform != 'other':
                platform_groups[platform].append(bookmark)
        
        suggestions = []
        for platform, bookmarks in platform_groups.items():
            if len(bookmarks) >= 5:  # Need significant content per platform
                confidence = min(0.70, len(bookmarks) / 15)
                platform_name = platform.title()
                suggestions.append({
                    'category': f"{platform_name} Collection",
                    'bookmarks': bookmarks,
                    'confidence': confidence,
                    'method': 'platform',
                    'description': f"Content from {platform_name} ({len(bookmarks)} videos)"
                })
        
        return suggestions
    
    def _analyze_by_content_type(self):
        """Categorize by content type (amateur, professional, etc.)"""
        content_groups = defaultdict(list)
        
        for bookmark in self.app.bookmarks:
            if bookmark.category != "Uncategorized":
                continue
            
            content_type = self._classify_content_type(bookmark.title.lower())
            if content_type:
                content_groups[content_type].append(bookmark)
        
        suggestions = []
        for content_type, bookmarks in content_groups.items():
            if len(bookmarks) >= 3:
                confidence = min(0.80, len(bookmarks) / 6)
                suggestions.append({
                    'category': content_type,
                    'bookmarks': bookmarks,
                    'confidence': confidence,
                    'method': 'content_type',
                    'description': f"{content_type} content ({len(bookmarks)} videos)"
                })
        
        return suggestions
    
    def _analyze_by_quality(self):
        """Group by video quality indicators"""
        quality_groups = defaultdict(list)
        
        for bookmark in self.app.bookmarks:
            if bookmark.category != "Uncategorized":
                continue
            
            quality = self._detect_quality(bookmark.title.lower())
            if quality:
                quality_groups[quality].append(bookmark)
        
        suggestions = []
        for quality, bookmarks in quality_groups.items():
            if len(bookmarks) >= 4:
                confidence = min(0.75, len(bookmarks) / 8)
                suggestions.append({
                    'category': f"{quality} Quality",
                    'bookmarks': bookmarks,
                    'confidence': confidence,
                    'method': 'quality',
                    'description': f"{quality} quality videos ({len(bookmarks)} videos)"
                })
        
        return suggestions
    
    def _analyze_by_duration(self):
        """Group by video duration patterns"""
        duration_groups = {'Quick Videos': [], 'Long Videos': []}
        
        for bookmark in self.app.bookmarks:
            if bookmark.category != "Uncategorized":
                continue
            
            title_lower = bookmark.title.lower()
            
            # Quick videos
            if any(word in title_lower for word in ['quick', 'short', 'brief', 'quickie']):
                duration_groups['Quick Videos'].append(bookmark)
            
            # Long videos  
            elif any(word in title_lower for word in ['full', 'complete', 'long', 'extended', 'full length']):
                duration_groups['Long Videos'].append(bookmark)
        
        suggestions = []
        for duration_type, bookmarks in duration_groups.items():
            if len(bookmarks) >= 5:
                confidence = min(0.70, len(bookmarks) / 10)
                suggestions.append({
                    'category': duration_type,
                    'bookmarks': bookmarks,
                    'confidence': confidence,
                    'method': 'duration',
                    'description': f"{duration_type.lower()} ({len(bookmarks)} videos)"
                })
        
        return suggestions
    
    def _analyze_by_viewing_behavior(self):
        """Suggest categories based on viewing patterns"""
        suggestions = []
        
        # Frequently viewed
        frequent = [b for b in self.app.bookmarks 
                   if b.category == "Uncategorized" and b.view_count >= 3]
        if len(frequent) >= 3:
            suggestions.append({
                'category': 'Frequently Watched',
                'bookmarks': frequent,
                'confidence': 0.85,
                'method': 'viewing_behavior',
                'description': f"Videos you watch often ({len(frequent)} videos)"
            })
        
        # Never viewed
        unviewed = [b for b in self.app.bookmarks 
                   if b.category == "Uncategorized" and b.view_count == 0]
        if len(unviewed) >= 10:
            suggestions.append({
                'category': 'Watch Later',
                'bookmarks': unviewed,
                'confidence': 0.75,
                'method': 'viewing_behavior',
                'description': f"Unwatched videos ({len(unviewed)} videos)"
            })
        
        return suggestions
    
    def _extract_performers(self, title):
        """Extract performer names from video title"""
        performers = []
        title_lower = title.lower()
        
        # Common patterns for performer names
        # This is a simplified version - real implementation would be more sophisticated
        
        # Look for "featuring X" or "with X" patterns
        for indicator in self.performer_indicators:
            if indicator in title_lower:
                parts = title_lower.split(indicator)
                if len(parts) > 1:
                    # Extract potential performer name after indicator
                    potential_name = parts[1].strip().split()[0:2]  # First 1-2 words
                    if potential_name:
                        name = ' '.join(potential_name).title()
                        if len(name) > 2 and len(name) < 30:  # Reasonable name length
                            performers.append(name)
        
        # Look for capitalized words (potential performer names)
        words = title.split()
        for i, word in enumerate(words):
            if (word[0].isupper() and len(word) > 2 and 
                not word.isupper() and  # Avoid all-caps words
                i < len(words) - 1 and words[i+1][0].isupper()):
                # Found potential first and last name
                name = f"{word} {words[i+1]}"
                if len(name) < 30:
                    performers.append(name)
        
        return list(set(performers))  # Remove duplicates
    
    def _extract_studio(self, title, url):
        """Extract studio/production company"""
        # Check URL for studio indicators
        domain = urlparse(url).netloc.lower()
        
        # Some studios have their own domains
        studio_domains = {
            'brazzers.com': 'Brazzers',
            'realitykings.com': 'Reality Kings',
            'bangbros.com': 'Bang Bros',
            'naughtyamerica.com': 'Naughty America'
        }
        
        for domain_pattern, studio in studio_domains.items():
            if domain_pattern in domain:
                return studio
        
        # Check title for studio mentions
        title_lower = title.lower()
        studios = ['brazzers', 'realitykings', 'bangbros', 'naughtyamerica', 'digitalplayground']
        
        for studio in studios:
            if studio in title_lower:
                return studio.title()
        
        return None
    
    def _classify_content_type(self, title_lower):
        """Classify content type from title"""
        for category, patterns in self.category_patterns.items():
            if 'keywords' in patterns:
                if any(keyword in title_lower for keyword in patterns['keywords']):
                    return category
        return None
    
    def _detect_quality(self, title_lower):
        """Detect video quality from title"""
        if any(q in title_lower for q in ['4k', 'uhd', '2160p']):
            return '4K/UHD'
        elif any(q in title_lower for q in ['1080p', 'full hd', 'fhd']):
            return 'Full HD'
        elif any(q in title_lower for q in ['720p', 'hd']):
            return 'HD'
        elif any(q in title_lower for q in ['480p', '360p', 'sd']):
            return 'SD'
        return None
    
    def _rank_suggestions(self, suggestions):
        """Rank suggestions by importance and confidence"""
        # Sort by: 1) Method priority, 2) Confidence, 3) Number of bookmarks
        method_priority = {
            'performer': 1,
            'viewing_behavior': 2,
            'content_type': 3,
            'studio': 4,
            'quality': 5,
            'duration': 6,
            'platform': 7
        }
        
        suggestions.sort(key=lambda x: (
            method_priority.get(x['method'], 10),
            -x['confidence'],
            -len(x['bookmarks'])
        ))
        
        return suggestions


# ==========================================
# MODERN UI FOR ADULT CONTENT CATEGORIZATION
# ==========================================

class AdultContentCategorizationDialog:
    """Specialized categorization dialog for adult content"""
    
    def __init__(self, app, parent):
        self.app = app
        self.parent = parent
        self.engine = AdultContentCategorizationEngine(app)
        self.suggestions = []
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Smart Adult Content Categorization")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.geometry("1000x750")
        
        self.create_widgets()
        self.analyze_content()
    
    def create_widgets(self):
        """Create specialized UI for adult content management"""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header with icon and title
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(
            header_frame,
            text="🎭 Smart Adult Content Categorization",
            font=("Arial", 16, "bold")
        )
        title_label.pack(side=tk.LEFT)
        
        # Quick stats
        self.stats_label = ttk.Label(header_frame, text="Analyzing...", font=("Arial", 10))
        self.stats_label.pack(side=tk.RIGHT)
        
        # Description
        desc_label = ttk.Label(
            main_frame,
            text="Intelligent categorization for adult content based on performers, studios, "
                 "content type, and viewing behavior. Select categories to organize your collection:",
            wraplength=950
        )
        desc_label.pack(fill=tk.X, pady=(0, 10))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        
        # Notebook for different category types
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create frames for different types
        self.performer_frame = ttk.Frame(self.notebook)
        self.content_frame = ttk.Frame(self.notebook)
        self.behavior_frame = ttk.Frame(self.notebook)
        self.technical_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.performer_frame, text="👥 Performers")
        self.notebook.add(self.content_frame, text="🎬 Content Type")
        self.notebook.add(self.behavior_frame, text="📊 Viewing Behavior")
        self.notebook.add(self.technical_frame, text="⚙️ Technical")
        
        # Create scrollable areas for each tab
        self.create_scrollable_frame(self.performer_frame, 'performers')
        self.create_scrollable_frame(self.content_frame, 'content')
        self.create_scrollable_frame(self.behavior_frame, 'behavior')
        self.create_scrollable_frame(self.technical_frame, 'technical')
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # Left side
        select_frame = ttk.Frame(button_frame)
        select_frame.pack(side=tk.LEFT)
        
        ttk.Button(select_frame, text="Select All", command=self.select_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(select_frame, text="Select Performers Only", command=self.select_performers).pack(side=tk.LEFT, padx=2)
        ttk.Button(select_frame, text="Select High Confidence", command=self.select_high_confidence).pack(side=tk.LEFT, padx=2)
        
        # Right side
        action_frame = ttk.Frame(button_frame)
        action_frame.pack(side=tk.RIGHT)
        
        ttk.Button(action_frame, text="Apply Selected", command=self.apply_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def create_scrollable_frame(self, parent, frame_type):
        """Create scrollable frame for suggestions"""
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Store reference to scrollable frame
        setattr(self, f'{frame_type}_scrollable', scrollable_frame)
    
    def analyze_content(self):
        """Analyze content and display suggestions"""
        self.progress.pack(fill=tk.X, pady=5)
        self.progress.start()
        
        self.dialog.update()
        
        try:
            self.suggestions = self.engine.analyze_bookmarks()
            self.progress.stop()
            self.progress.pack_forget()
            
            self.display_suggestions()
            self.update_stats()
            
        except Exception as e:
            self.progress.stop()
            self.progress.pack_forget()
            messagebox.showerror("Error", f"Analysis failed: {e}")
    
    def display_suggestions(self):
        """Display suggestions organized by type"""
        self.suggestion_vars = []
        
        # Group suggestions by method
        suggestion_groups = {
            'performers': [],
            'content': [],
            'behavior': [],
            'technical': []
        }
        
        for suggestion in self.suggestions:
            method = suggestion['method']
            if method == 'performer':
                suggestion_groups['performers'].append(suggestion)
            elif method in ['content_type', 'studio']:
                suggestion_groups['content'].append(suggestion)
            elif method == 'viewing_behavior':
                suggestion_groups['behavior'].append(suggestion)
            else:  # platform, quality, duration
                suggestion_groups['technical'].append(suggestion)
        
        # Display in appropriate tabs
        self.display_suggestions_in_tab(suggestion_groups['performers'], self.performers_scrollable, '👤')
        self.display_suggestions_in_tab(suggestion_groups['content'], self.content_scrollable, '🎬')
        self.display_suggestions_in_tab(suggestion_groups['behavior'], self.behavior_scrollable, '📊')
        self.display_suggestions_in_tab(suggestion_groups['technical'], self.technical_scrollable, '⚙️')
    
    def display_suggestions_in_tab(self, suggestions, parent_frame, icon):
        """Display suggestions in a specific tab"""
        if not suggestions:
            no_suggestions = ttk.Label(
                parent_frame,
                text=f"No {icon} suggestions found for this content type",
                font=("Arial", 10),
                foreground="gray"
            )
            no_suggestions.pack(pady=20)
            return
        
        for suggestion in suggestions:
            self.create_suggestion_widget(suggestion, parent_frame, icon)
    
    def create_suggestion_widget(self, suggestion, parent, icon):
        """Create enhanced suggestion widget for adult content"""
        # Main frame with better styling
        suggestion_frame = ttk.LabelFrame(parent, padding=10)
        suggestion_frame.pack(fill=tk.X, padx=5, pady=8)
        
        # Header with checkbox and category info
        header_frame = ttk.Frame(suggestion_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        var = tk.BooleanVar()
        # Auto-select high confidence suggestions, especially performers
        if (suggestion['confidence'] > 0.8 or 
            suggestion['method'] == 'performer' and suggestion['confidence'] > 0.7):
            var.set(True)
        
        self.suggestion_vars.append(var)
        
        checkbox = ttk.Checkbutton(header_frame, variable=var)
        checkbox.pack(side=tk.LEFT)
        
        # Category name with confidence and method indicators
        confidence_text = f"{suggestion['confidence']:.0%}"
        confidence_color = self.get_confidence_color(suggestion['confidence'])
        
        # Special handling for performer categories
        if suggestion['method'] == 'performer':
            icon = "👤"
            priority_text = " ⭐ HIGH PRIORITY" if len(suggestion['bookmarks']) >= 5 else ""
        else:
            priority_text = ""
        
        title_text = f"{icon} {suggestion['category']} ({confidence_text}){priority_text}"
        title_label = ttk.Label(
            header_frame,
            text=title_text,
            font=("Arial", 11, "bold")
        )
        title_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Auto-apply indicator for high-value categories
        if suggestion.get('auto_apply', False):
            auto_label = ttk.Label(
                header_frame,
                text="🚀 AUTO-APPLY",
                font=("Arial", 8),
                foreground="green"
            )
            auto_label.pack(side=tk.RIGHT)
        
        # Description with enhanced details
        desc_frame = ttk.Frame(suggestion_frame)
        desc_frame.pack(fill=tk.X, pady=(0, 5))
        
        desc_text = f"{suggestion['description']} • Analysis: {suggestion['method']}"
        
        # Add special notes for different types
        if suggestion['method'] == 'performer':
            desc_text += " • 🔥 Performer collections are highly recommended"
        elif suggestion['method'] == 'viewing_behavior':
            desc_text += " • 📈 Based on your viewing patterns"
        elif suggestion['method'] == 'studio':
            desc_text += " • 🏢 Professional studio content"
        
        desc_label = ttk.Label(desc_frame, text=desc_text, font=("Arial", 9))
        desc_label.pack(side=tk.LEFT)
        
        # Enhanced preview with video count and quality info
        preview_frame = ttk.Frame(suggestion_frame)
        preview_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Sample titles
        sample_bookmarks = suggestion['bookmarks'][:2]
        sample_text = "Examples: " + " • ".join([
            b.title[:40] + "..." if len(b.title) > 40 else b.title 
            for b in sample_bookmarks
        ])
        
        if len(suggestion['bookmarks']) > 2:
            sample_text += f" • +{len(suggestion['bookmarks']) - 2} more videos"
        
        preview_label = ttk.Label(
            preview_frame,
            text=sample_text,
            font=("Arial", 8),
            foreground="gray",
            wraplength=900
        )
        preview_label.pack(side=tk.LEFT)
        
        # Enhanced stats for adult content
        stats_frame = ttk.Frame(suggestion_frame)
        stats_frame.pack(fill=tk.X)
        
        # Calculate useful stats
        total_views = sum(b.view_count for b in suggestion['bookmarks'])
        platforms = set(b.platform for b in suggestion['bookmarks'])
        avg_rating = sum(b.adult_metadata.personal_rating or 0 for b in suggestion['bookmarks']) / len(suggestion['bookmarks'])
        
        stats_text = f"📊 {len(suggestion['bookmarks'])} videos • {total_views} total views"
        if len(platforms) > 1:
            stats_text += f" • {len(platforms)} platforms"
        if avg_rating > 0:
            stats_text += f" • ⭐ {avg_rating:.1f} avg rating"
        
        stats_label = ttk.Label(
            stats_frame,
            text=stats_text,
            font=("Arial", 8),
            foreground="blue"
        )
        stats_label.pack(side=tk.LEFT)
        
        # Action buttons for this category
        action_frame = ttk.Frame(stats_frame)
        action_frame.pack(side=tk.RIGHT)
        
        # Preview button
        def preview_category():
            self.show_category_preview(suggestion)
        
        ttk.Button(
            action_frame,
            text="👁️ Preview",
            command=preview_category
        ).pack(side=tk.LEFT, padx=2)
        
        # Quick apply button for high-confidence suggestions
        if suggestion['confidence'] > 0.8:
            def quick_apply():
                self.quick_apply_category(suggestion)
            
            ttk.Button(
                action_frame,
                text="⚡ Quick Apply",
                command=quick_apply
            ).pack(side=tk.LEFT, padx=2)
    
    def get_confidence_color(self, confidence):
        """Get color indicator for confidence level"""
        if confidence >= 0.85:
            return "green"
        elif confidence >= 0.7:
            return "orange"
        else:
            return "red"
    
    def update_stats(self):
        """Update statistics display"""
        uncategorized = [b for b in self.app.bookmarks if b.category == "Uncategorized"]
        performer_suggestions = [s for s in self.suggestions if s['method'] == 'performer']
        high_confidence = [s for s in self.suggestions if s['confidence'] > 0.8]
        
        potential_categorized = sum(len(s['bookmarks']) for s in self.suggestions)
        
        stats_text = (
            f"📊 {len(uncategorized)} uncategorized • "
            f"👥 {len(performer_suggestions)} performers • "
            f"⭐ {len(high_confidence)} high confidence • "
            f"📈 {potential_categorized} videos ready to organize"
        )
        
        self.stats_label.config(text=stats_text)
    
    def show_category_preview(self, suggestion):
        """Show detailed preview of category contents"""
        preview_window = tk.Toplevel(self.dialog)
        preview_window.title(f"Preview: {suggestion['category']}")
        preview_window.geometry("800x600")
        preview_window.transient(self.dialog)
        
        # Header
        header_label = ttk.Label(
            preview_window,
            text=f"📋 Preview: {suggestion['category']}",
            font=("Arial", 14, "bold")
        )
        header_label.pack(pady=10)
        
        # Description
        desc_label = ttk.Label(
            preview_window,
            text=suggestion['description'],
            font=("Arial", 10)
        )
        desc_label.pack(pady=5)
        
        # Video list
        list_frame = ttk.Frame(preview_window)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for videos
        columns = ("title", "platform", "views", "rating")
        tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        tree.heading("title", text="Title")
        tree.heading("platform", text="Platform")
        tree.heading("views", text="Views")
        tree.heading("rating", text="Rating")
        
        tree.column("title", width=400)
        tree.column("platform", width=100)
        tree.column("views", width=80)
        tree.column("rating", width=80)
        
        # Add videos
        for bookmark in suggestion['bookmarks']:
            rating = bookmark.adult_metadata.personal_rating or ""
            tree.insert("", tk.END, values=(
                bookmark.title,
                bookmark.platform.title(),
                bookmark.view_count,
                f"⭐{rating}" if rating else ""
            ))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Close button
        ttk.Button(
            preview_window,
            text="Close",
            command=preview_window.destroy
        ).pack(pady=10)
    
    def quick_apply_category(self, suggestion):
        """Quickly apply a single category"""
        if messagebox.askyesno(
            "Quick Apply",
            f"Apply category '{suggestion['category']}' to {len(suggestion['bookmarks'])} videos?"
        ):
            # Create category
            self.app.link_controller._ensure_category_exists(suggestion['category'])
            
            # Categorize bookmarks
            for bookmark in suggestion['bookmarks']:
                if bookmark.category == "Uncategorized":
                    self.app.link_controller.update_bookmark(bookmark, category=suggestion['category'])
            
            messagebox.showinfo(
                "Applied",
                f"Successfully categorized {len(suggestion['bookmarks'])} videos as '{suggestion['category']}'"
            )
            
            # Refresh the dialog
            self.analyze_content()
    
    def select_all(self):
        """Select all suggestions"""
        for var in self.suggestion_vars:
            var.set(True)
    
    def select_performers(self):
        """Select only performer-based suggestions"""
        for i, var in enumerate(self.suggestion_vars):
            if i < len(self.suggestions):
                var.set(self.suggestions[i]['method'] == 'performer')
    
    def select_high_confidence(self):
        """Select high confidence suggestions"""
        for i, var in enumerate(self.suggestion_vars):
            if i < len(self.suggestions):
                var.set(self.suggestions[i]['confidence'] > 0.8)
    
    def apply_selected(self):
        """Apply all selected categorization suggestions"""
        selected_count = 0
        categorized_count = 0
        
        for i, var in enumerate(self.suggestion_vars):
            if var.get() and i < len(self.suggestions):
                suggestion = self.suggestions[i]
                selected_count += 1
                
                # Create category
                self.app.link_controller._ensure_category_exists(suggestion['category'])
                
                # Categorize bookmarks
                for bookmark in suggestion['bookmarks']:
                    if bookmark.category == "Uncategorized":
                        self.app.link_controller.update_bookmark(bookmark, category=suggestion['category'])
                        categorized_count += 1
        
        if selected_count == 0:
            messagebox.showwarning("No Selection", "Please select at least one category to apply.")
            return
        
        # Success message with recommendations
        success_msg = (
            f"🎉 Successfully organized your adult content!\n\n"
            f"✅ Applied {selected_count} categorization rules\n"
            f"📂 Categorized {categorized_count} videos\n\n"
            f"💡 Tip: Performer-based categories are most useful for discovering content.\n"
            f"Consider rating your favorites to improve future recommendations!"
        )
        
        messagebox.showinfo("Categorization Complete", success_msg)
        self.dialog.destroy()


# ==========================================
# INTEGRATION WITH MAIN APPLICATION
# ==========================================

class AdultContentManager:
    """Main manager class for adult content features"""
    
    def __init__(self, app):
        self.app = app
        
    def smart_categorize(self):
        """Launch smart categorization for adult content"""
        if not self.app.bookmarks:
            messagebox.showwarning("No Content", "No bookmarks loaded to categorize.")
            return
        
        # Check for uncategorized content
        uncategorized = [b for b in self.app.bookmarks if b.category == "Uncategorized"]
        if not uncategorized:
            messagebox.showinfo(
                "Already Organized",
                "🎉 All your content is already categorized!\n\n"
                "Your adult content collection is well organized. "
                "Add more bookmarks to use auto-categorization again."
            )
            return
        
        # Launch categorization dialog
        dialog = AdultContentCategorizationDialog(self.app, self.app.root)
    
    def create_essential_collections(self):
        """Create essential collections for adult content management"""
        essential_collections = [
            "⭐ Favorites",
            "📺 Watch Later", 
            "🔥 Frequently Watched",
            "📱 Mobile Friendly",
            "🎬 High Quality",
            "⚡ Quick Videos",
            "🕐 Long Form Content"
        ]
        
        created_count = 0
        for collection in essential_collections:
            if not any(c.name == collection for c in self.app.categories):
                self.app.link_controller._ensure_category_exists(collection)
                created_count += 1
        
        if created_count > 0:
            messagebox.showinfo(
                "Collections Created",
                f"Created {created_count} essential collections for organizing your adult content.\n\n"
                "Use these to organize your content by purpose and preference!"
            )
    
    def analyze_collection_stats(self):
        """Provide analytics about the adult content collection"""
        if not self.app.bookmarks:
            messagebox.showwarning("No Content", "No bookmarks to analyze.")
            return
        
        # Calculate statistics
        total_videos = len(self.app.bookmarks)
        total_views = sum(b.view_count for b in self.app.bookmarks)
        platforms = Counter(b.platform for b in self.app.bookmarks)
        categories = Counter(b.category for b in self.app.bookmarks)
        
        # Create analytics window
        analytics_window = tk.Toplevel(self.app.root)
        analytics_window.title("📊 Collection Analytics")
        analytics_window.geometry("600x500")
        
        # Header
        header_label = ttk.Label(
            analytics_window,
            text="📊 Your Adult Content Collection Analytics",
            font=("Arial", 16, "bold")
        )
        header_label.pack(pady=10)
        
        # Stats text
        stats_text = f"""
📈 Collection Overview:
• Total Videos: {total_videos}
• Total Views: {total_views}
• Average Views per Video: {total_views/total_videos:.1f}

🌐 Top Platforms:
"""
        for platform, count in platforms.most_common(5):
            percentage = (count/total_videos)*100
            stats_text += f"• {platform.title()}: {count} videos ({percentage:.1f}%)\n"
        
        stats_text += f"\n📂 Categories:\n"
        for category, count in categories.most_common(10):
            percentage = (count/total_videos)*100
            stats_text += f"• {category}: {count} videos ({percentage:.1f}%)\n"
        
        # Display stats
        text_widget = tk.Text(analytics_window, wrap=tk.WORD, font=("Arial", 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, stats_text)
        text_widget.config(state=tk.DISABLED)
        
        # Close button
        ttk.Button(
            analytics_window,
            text="Close",
            command=analytics_window.destroy
        ).pack(pady=10)


# ==========================================
# UPDATED KEYWORD CONTROLLER FOR ADULT CONTENT
# ==========================================

class AdultContentKeywordController:
    """Enhanced keyword controller specialized for adult content"""
    
    def __init__(self, app):
        self.app = app
        self.content_manager = AdultContentManager(app)
    
    def smart_auto_categorize(self):
        """Launch smart categorization specifically for adult content"""
        return self.content_manager.smart_categorize()
    
    def auto_categorize_bookmarks(self):
        """Legacy method - redirects to smart categorization"""
        return self.smart_auto_categorize()
    
    def extract_keywords(self):
        """Legacy method for backward compatibility"""
        messagebox.showinfo(
            "Enhanced Categorization Available",
            "🚀 A more powerful categorization system is now available!\n\n"
            "The new system recognizes:\n"
            "• Performer names and creates collections\n"
            "• Content types and quality levels\n"
            "• Studios and production companies\n"
            "• Viewing behavior patterns\n\n"
            "Click 'Smart Auto-Categorize' for the enhanced experience!"
        )
        return []


def integrate_adult_content_manager(app):
    """
    Integration function to upgrade existing bookmark manager for adult content.
    Call this to enable adult content management features.
    """
    # Replace bookmark class with adult-enhanced version
    # This would require updating your existing bookmarks - see migration below
    
    # Replace keyword controller
    app.keyword_controller = AdultContentKeywordController(app)
    
    # Add content manager
    app.adult_content_manager = AdultContentManager(app)
    
    return app


def migrate_existing_bookmarks_to_adult_format(app):
    """
    Migrate existing bookmarks to adult content format.
    This preserves all existing data while adding adult-specific features.
    """
    migrated_bookmarks = []
    
    for old_bookmark in app.bookmarks:
        # Create new adult bookmark
        adult_bookmark = AdultBookmark(
            url=old_bookmark.url,
            title=old_bookmark.title,
            category=getattr(old_bookmark, 'category', 'Uncategorized')
        )
        
        # Preserve existing data
        if hasattr(old_bookmark, 'rating'):
            adult_bookmark.adult_metadata.personal_rating = old_bookmark.rating
        
        if hasattr(old_bookmark, 'keywords'):
            adult_bookmark.adult_metadata.content_tags = old_bookmark.keywords
        
        if hasattr(old_bookmark, 'date_added'):
            adult_bookmark.date_added = old_bookmark.date_added
        
        # Initialize platform detection
        adult_bookmark.platform = adult_bookmark._detect_platform()
        adult_bookmark.platform_id = adult_bookmark._extract_platform_id()
        
        migrated_bookmarks.append(adult_bookmark)
    
    app.bookmarks = migrated_bookmarks
    return len(migrated_bookmarks)


# ==========================================
# EXAMPLE USAGE AND TESTING
# ==========================================

def demo_adult_content_manager():
    """Demo function showing the adult content manager in action"""
    
    # Create demo app with sample adult bookmarks
    class DemoApp:
        def __init__(self):
            self.bookmarks = [
                AdultBookmark(
                    "https://www.pornhub.com/view_video.php?viewkey=ph123456",
                    "Amazing Performance by Riley Reid - HD Quality",
                    "Uncategorized"
                ),
                AdultBookmark(
                    "https://www.pornhub.com/view_video.php?viewkey=ph789012",
                    "Riley Reid and Johnny Sins - Professional Scene",
                    "Uncategorized"
                ),
                AdultBookmark(
                    "https://www.xvideos.com/video123/amateur_couple_homemade",
                    "Real Amateur Couple - Homemade Content",
                    "Uncategorized"
                ),
                AdultBookmark(
                    "https://www.xhamster.com/videos/4k-ultra-hd-premium",
                    "Ultra HD 4K Premium Professional Content",
                    "Uncategorized"
                ),
                AdultBookmark(
                    "https://www.spankbang.com/quick-video/video/",
                    "Quick 5 Minute Solo Performance",
                    "Uncategorized"
                )
            ]
            
            # Add some viewing history to demonstrate behavior analysis
            self.bookmarks[0].add_view_session(duration_watched=1200, completion_rate=0.8)
            self.bookmarks[0].add_view_session(duration_watched=1500, completion_rate=1.0)
            self.bookmarks[1].add_view_session(duration_watched=900, completion_rate=0.6)
            
            self.categories = []
            self.root = tk.Tk()
            self.root.title("Adult Content Manager Demo")
            
            # Mock link controller
            self.link_controller = type('LinkController', (), {
                '_ensure_category_exists': lambda self, name: None,
                'update_bookmark': lambda self, bookmark, **kwargs: setattr(bookmark, 'category', kwargs.get('category', bookmark.category))
            })()
    
    # Create and run demo
    app = DemoApp()
    
    # Integrate adult content management
    integrate_adult_content_manager(app)
    
    # Launch categorization
    app.adult_content_manager.smart_categorize()
    
    # Run demo
    app.root.mainloop()


if __name__ == "__main__":
    # Uncomment to run demo
    # demo_adult_content_manager()
    pass
