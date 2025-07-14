from datetime import datetime, timedelta
from urllib.parse import urlparse
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import json

@dataclass
class AdultVideoMetadata:
    """Metadata specific to adult video content"""
    performers: List[str] = field(default_factory=list)
    studio: Optional[str] = None
    duration: Optional[str] = None  # Format: "MM:SS" or "HH:MM:SS"
    resolution: Optional[str] = None  # "1080p", "720p", "4K", etc.
    file_size: Optional[str] = None
    video_quality: Optional[str] = None  # "HD", "4K", "SD"
    content_tags: List[str] = field(default_factory=list)
    favorite_scenes: List[Dict[str, Any]] = field(default_factory=list)
    thumbnail_path: Optional[str] = None
    is_favorite: bool = False
    privacy_level: str = "private"  # "private", "discrete", "hidden"
    
    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            'performers': self.performers,
            'studio': self.studio,
            'duration': self.duration,
            'resolution': self.resolution,
            'file_size': self.file_size,
            'video_quality': self.video_quality,
            'content_tags': self.content_tags,
            'favorite_scenes': self.favorite_scenes,
            'thumbnail_path': self.thumbnail_path,
            'is_favorite': self.is_favorite,
            'privacy_level': self.privacy_level
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        return cls(
            performers=data.get('performers', []),
            studio=data.get('studio'),
            duration=data.get('duration'),
            resolution=data.get('resolution'),
            file_size=data.get('file_size'),
            video_quality=data.get('video_quality'),
            content_tags=data.get('content_tags', []),
            favorite_scenes=data.get('favorite_scenes', []),
            thumbnail_path=data.get('thumbnail_path'),
            is_favorite=data.get('is_favorite', False),
            privacy_level=data.get('privacy_level', 'private')
        )
    
    def add_favorite_scene(self, timestamp: str, description: str = ""):
        """Add a favorite scene timestamp"""
        scene = {
            'timestamp': timestamp,
            'description': description,
            'added': datetime.now().isoformat()
        }
        self.favorite_scenes.append(scene)
    
    def remove_favorite_scene(self, timestamp: str):
        """Remove a favorite scene by timestamp"""
        self.favorite_scenes = [
            scene for scene in self.favorite_scenes 
            if scene['timestamp'] != timestamp
        ]

class EnhancedBookmark:
    """Enhanced bookmark with adult content support"""
    
    def __init__(self, url, title, category="Uncategorized", rating=None):
        # Basic properties (maintaining compatibility)
        self.url = url
        self.title = title
        self.category = category
        self.rating = rating
        self.keywords = []
        
        # Enhanced properties
        self.date_added = datetime.now()
        self.date_modified = datetime.now()
        
        # Adult content specific
        self.adult_metadata = AdultVideoMetadata()
        self.view_count = 0
        self.last_viewed = None
        self.view_history = []  # List of viewing session data
        self.collections = []  # Custom collections this video belongs to
        self.notes = ""  # Private notes
        
        # Download tracking
        self.is_downloaded = False
        self.local_file_path = None
        self.download_date = None
        
        # Privacy and security
        self.access_level = "normal"  # "normal", "restricted", "hidden"
        self.password_protected = False
        self.encrypted_data = None
        
        # Platform detection and metadata
        self.platform = self._detect_platform()
        self.platform_id = None  # Platform-specific video ID
        
        # Analytics
        self.total_watch_time = 0  # Total seconds watched
        self.completion_rate = 0.0  # Percentage of video watched
        
    def _detect_platform(self):
        """Detect adult video platform from URL"""
        if not self.url:
            return 'unknown'
            
        domain = urlparse(self.url).netloc.lower()
        
        # Remove www. prefix for consistency
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Common adult platforms
        adult_platforms = {
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
            'porndig.com': 'porndig',
            'txxx.com': 'txxx'
        }
        
        for platform_domain, platform_name in adult_platforms.items():
            if platform_domain in domain:
                return platform_name
                
        return 'other'
    
    def add_view_session(self, duration_watched=None, completion_rate=None):
        """Record a viewing session"""
        self.view_count += 1
        self.last_viewed = datetime.now()
        
        session_data = {
            'timestamp': datetime.now().isoformat(),
            'duration_watched': duration_watched,
            'completion_rate': completion_rate
        }
        
        self.view_history.append(session_data)
        
        # Update analytics
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
    
    def remove_from_collection(self, collection_name):
        """Remove from a collection"""
        if collection_name in self.collections:
            self.collections.remove(collection_name)
            self.date_modified = datetime.now()
    
    def mark_as_downloaded(self, file_path):
        """Mark as downloaded with file path"""
        self.is_downloaded = True
        self.local_file_path = file_path
        self.download_date = datetime.now()
    
    def get_view_frequency(self, days=30):
        """Get viewing frequency over specified days"""
        if not self.view_history:
            return 0
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_views = [
            view for view in self.view_history
            if datetime.fromisoformat(view['timestamp']) > cutoff_date
        ]
        
        return len(recent_views) / days if days > 0 else 0
    
    def get_total_watch_time_formatted(self):
        """Get formatted total watch time"""
        if self.total_watch_time < 60:
            return f"{int(self.total_watch_time)}s"
        elif self.total_watch_time < 3600:
            minutes = int(self.total_watch_time // 60)
            seconds = int(self.total_watch_time % 60)
            return f"{minutes}m {seconds}s"
        else:
            hours = int(self.total_watch_time // 3600)
            minutes = int((self.total_watch_time % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    def to_dict(self):
        """Convert the bookmark to a dictionary for serialization"""
        return {
            "url": self.url,
            "title": self.title,
            "category": self.category,
            "rating": self.rating,
            "keywords": self.keywords,
            "date_added": self.date_added.isoformat(),
            "date_modified": self.date_modified.isoformat(),
            "adult_metadata": self.adult_metadata.to_dict(),
            "view_count": self.view_count,
            "last_viewed": self.last_viewed.isoformat() if self.last_viewed else None,
            "view_history": self.view_history,
            "collections": self.collections,
            "notes": self.notes,
            "is_downloaded": self.is_downloaded,
            "local_file_path": self.local_file_path,
            "download_date": self.download_date.isoformat() if self.download_date else None,
            "access_level": self.access_level,
            "password_protected": self.password_protected,
            "platform": self.platform,
            "platform_id": self.platform_id,
            "total_watch_time": self.total_watch_time,
            "completion_rate": self.completion_rate
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a bookmark from a dictionary"""
        bookmark = cls(
            url=data["url"],
            title=data["title"],
            category=data.get("category", "Uncategorized"),
            rating=data.get("rating")
        )
        
        # Set additional properties
        bookmark.keywords = data.get("keywords", [])
        
        # Parse dates
        if "date_added" in data:
            bookmark.date_added = datetime.fromisoformat(data["date_added"])
        if "date_modified" in data:
            bookmark.date_modified = datetime.fromisoformat(data["date_modified"])
        if "last_viewed" in data and data["last_viewed"]:
            bookmark.last_viewed = datetime.fromisoformat(data["last_viewed"])
        if "download_date" in data and data["download_date"]:
            bookmark.download_date = datetime.fromisoformat(data["download_date"])
        
        # Set adult metadata
        if "adult_metadata" in data:
            bookmark.adult_metadata = AdultVideoMetadata.from_dict(data["adult_metadata"])
        
        # Set other properties
        bookmark.view_count = data.get("view_count", 0)
        bookmark.view_history = data.get("view_history", [])
        bookmark.collections = data.get("collections", [])
        bookmark.notes = data.get("notes", "")
        bookmark.is_downloaded = data.get("is_downloaded", False)
        bookmark.local_file_path = data.get("local_file_path")
        bookmark.access_level = data.get("access_level", "normal")
        bookmark.password_protected = data.get("password_protected", False)
        bookmark.platform = data.get("platform", bookmark._detect_platform())
        bookmark.platform_id = data.get("platform_id")
        bookmark.total_watch_time = data.get("total_watch_time", 0)
        bookmark.completion_rate = data.get("completion_rate", 0.0)
        
        return bookmark
    
    def __str__(self):
        """String representation of the bookmark"""
        return f"{self.title} ({self.url})"
    
    def __repr__(self):
        """Representation of the bookmark for debugging"""
        return f"EnhancedBookmark(url='{self.url}', title='{self.title}', platform='{self.platform}')"

# Backward compatibility - create an alias
Bookmark = EnhancedBookmark

# Migration utility
def migrate_old_bookmark_to_enhanced(old_bookmark):
    """Migrate an old bookmark object to enhanced bookmark"""
    enhanced = EnhancedBookmark(
        url=old_bookmark.url,
        title=old_bookmark.title,
        category=getattr(old_bookmark, 'category', 'Uncategorized'),
        rating=getattr(old_bookmark, 'rating', None)
    )
    
    # Copy over any existing keywords
    if hasattr(old_bookmark, 'keywords'):
        enhanced.keywords = old_bookmark.keywords
    
    return enhanced