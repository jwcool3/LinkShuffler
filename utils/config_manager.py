# Configuration management system

import json
import os
import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class AppConfig:
    """Application configuration class"""
    # Window settings
    window_width: int = 1000
    window_height: int = 700
    window_maximized: bool = False
    
    # Display settings
    default_page_size: int = 50
    theme: str = "clam"
    font_family: str = "Arial"
    font_size: int = 10
    
    # Auto-save settings
    auto_save_enabled: bool = True
    auto_save_interval: int = 300  # seconds
    auto_save_filename: str = "auto_save.json"
    backup_count: int = 5
    
    # Search settings
    search_fuzzy_threshold: float = 0.6
    search_case_sensitive: bool = False
    search_regex_enabled: bool = False
    max_search_history: int = 20
    
    # Performance settings
    use_search_indexing: bool = True
    use_lazy_loading: bool = True
    lazy_loading_threshold: int = 100
    use_database_mode: bool = False
    search_debounce_delay: int = 300  # milliseconds
    max_groups_display: int = 20
    max_bookmarks_per_group: int = 10
    background_processing: bool = True
    
    # TF-IDF settings
    tfidf_threshold: float = 0.1
    min_document_frequency: int = 2
    max_document_frequency: float = 0.8
    
    # Recent files
    recent_files: list = None
    max_recent_files: int = 10
    
    # UI preferences
    show_tooltips: bool = True
    confirm_deletions: bool = True
    show_status_bar: bool = True
    enhanced_mode_default: bool = False
    show_performance_monitor: bool = True
    
    def __post_init__(self):
        if self.recent_files is None:
            self.recent_files = []

class ConfigManager:
    """Configuration manager for the application"""
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = AppConfig()
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    # Update config with loaded data
                    for key, value in data.items():
                        if hasattr(self.config, key):
                            setattr(self.config, key, value)
            except Exception as e:
                print(f"Error loading config: {e}")
                # Use defaults
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(asdict(self.config), f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return getattr(self.config, key, default)
    
    def set(self, key: str, value):
        """Set configuration value"""
        if hasattr(self.config, key):
            setattr(self.config, key, value)
            self.save_config()
    
    def add_recent_file(self, filepath: str):
        """Add file to recent files list"""
        if filepath in self.config.recent_files:
            self.config.recent_files.remove(filepath)
        
        self.config.recent_files.insert(0, filepath)
        
        # Limit list size
        if len(self.config.recent_files) > self.config.max_recent_files:
            self.config.recent_files = self.config.recent_files[:self.config.max_recent_files]
        
        self.save_config()
    
    def get_recent_files(self):
        """Get list of recent files (filter out non-existent)"""
        return [f for f in self.config.recent_files if os.path.exists(f)]

# Settings dialog
class SettingsDialog:
    """Settings dialog for user preferences"""
    
    def __init__(self, parent, config_manager):
        self.parent = parent
        self.config_manager = config_manager
        self.config = config_manager.config
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Settings")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.geometry("500x600")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create settings dialog widgets"""
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # General settings
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="General")
        
        # Window settings
        window_group = ttk.LabelFrame(general_frame, text="Window")
        window_group.pack(fill=tk.X, padx=5, pady=5)
        
        # Theme selection
        ttk.Label(window_group, text="Theme:").pack(anchor=tk.W, padx=5, pady=2)
        self.theme_var = tk.StringVar(value=self.config.theme)
        theme_combo = ttk.Combobox(window_group, textvariable=self.theme_var,
                                  values=["clam", "alt", "default", "classic"],
                                  state="readonly")
        theme_combo.pack(anchor=tk.W, padx=5, pady=2)
        
        # Font settings
        font_group = ttk.LabelFrame(general_frame, text="Font")
        font_group.pack(fill=tk.X, padx=5, pady=5)
        
        font_frame = ttk.Frame(font_group)
        font_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(font_frame, text="Family:").pack(side=tk.LEFT)
        self.font_family_var = tk.StringVar(value=self.config.font_family)
        font_family_combo = ttk.Combobox(font_frame, textvariable=self.font_family_var,
                                        values=["Arial", "Helvetica", "Times", "Courier"],
                                        width=15)
        font_family_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(font_frame, text="Size:").pack(side=tk.LEFT, padx=(10, 0))
        self.font_size_var = tk.IntVar(value=self.config.font_size)
        font_size_spin = ttk.Spinbox(font_frame, from_=8, to=16,
                                    textvariable=self.font_size_var, width=5)
        font_size_spin.pack(side=tk.LEFT, padx=5)
        
        # Auto-save settings
        auto_save_frame = ttk.Frame(notebook)
        notebook.add(auto_save_frame, text="Auto-save")
        
        # Auto-save enabled
        self.auto_save_var = tk.BooleanVar(value=self.config.auto_save_enabled)
        ttk.Checkbutton(auto_save_frame, text="Enable auto-save",
                       variable=self.auto_save_var).pack(anchor=tk.W, padx=5, pady=5)
        
        # Auto-save interval
        interval_frame = ttk.Frame(auto_save_frame)
        interval_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(interval_frame, text="Interval (seconds):").pack(side=tk.LEFT)
        self.interval_var = tk.IntVar(value=self.config.auto_save_interval)
        ttk.Spinbox(interval_frame, from_=60, to=3600, textvariable=self.interval_var,
                   width=10).pack(side=tk.LEFT, padx=5)
        
        # Search settings
        search_frame = ttk.Frame(notebook)
        notebook.add(search_frame, text="Search")
        
        # Fuzzy threshold
        fuzzy_frame = ttk.Frame(search_frame)
        fuzzy_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(fuzzy_frame, text="Fuzzy search threshold:").pack(side=tk.LEFT)
        self.fuzzy_var = tk.DoubleVar(value=self.config.search_fuzzy_threshold)
        ttk.Scale(fuzzy_frame, from_=0.1, to=1.0, variable=self.fuzzy_var,
                 orient=tk.HORIZONTAL).pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # Case sensitive
        self.case_var = tk.BooleanVar(value=self.config.search_case_sensitive)
        ttk.Checkbutton(search_frame, text="Case sensitive search by default",
                       variable=self.case_var).pack(anchor=tk.W, padx=5, pady=5)
        
        # Performance settings
        perf_frame = ttk.Frame(notebook)
        notebook.add(perf_frame, text="Performance")
        
        # Search indexing
        self.indexing_var = tk.BooleanVar(value=self.config.use_search_indexing)
        ttk.Checkbutton(perf_frame, text="Enable search indexing (faster search for large collections)",
                       variable=self.indexing_var).pack(anchor=tk.W, padx=5, pady=5)
        
        # Lazy loading
        self.lazy_loading_var = tk.BooleanVar(value=self.config.use_lazy_loading)
        ttk.Checkbutton(perf_frame, text="Enable lazy loading (better performance for large collections)",
                       variable=self.lazy_loading_var).pack(anchor=tk.W, padx=5, pady=5)
        
        # Lazy loading threshold
        threshold_frame = ttk.Frame(perf_frame)
        threshold_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(threshold_frame, text="Lazy loading threshold (bookmarks):").pack(side=tk.LEFT)
        self.threshold_var = tk.IntVar(value=self.config.lazy_loading_threshold)
        ttk.Spinbox(threshold_frame, from_=50, to=1000, textvariable=self.threshold_var,
                   width=10).pack(side=tk.LEFT, padx=5)
        
        # Page size
        page_frame = ttk.Frame(perf_frame)
        page_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(page_frame, text="Default page size:").pack(side=tk.LEFT)
        self.page_size_var = tk.IntVar(value=self.config.default_page_size)
        ttk.Spinbox(page_frame, from_=25, to=200, textvariable=self.page_size_var,
                   width=10).pack(side=tk.LEFT, padx=5)
        
        # Search debounce delay
        debounce_frame = ttk.Frame(perf_frame)
        debounce_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(debounce_frame, text="Search debounce delay (ms):").pack(side=tk.LEFT)
        self.debounce_var = tk.IntVar(value=self.config.search_debounce_delay)
        ttk.Spinbox(debounce_frame, from_=100, to=1000, textvariable=self.debounce_var,
                   width=10).pack(side=tk.LEFT, padx=5)
        
        # Background processing
        self.background_var = tk.BooleanVar(value=self.config.background_processing)
        ttk.Checkbutton(perf_frame, text="Enable background processing",
                       variable=self.background_var).pack(anchor=tk.W, padx=5, pady=5)
        
        # Performance monitor
        self.perf_monitor_var = tk.BooleanVar(value=self.config.show_performance_monitor)
        ttk.Checkbutton(perf_frame, text="Show performance monitor",
                       variable=self.perf_monitor_var).pack(anchor=tk.W, padx=5, pady=5)
        
        # UI Preferences
        ui_frame = ttk.Frame(notebook)
        notebook.add(ui_frame, text="Interface")
        
        self.tooltips_var = tk.BooleanVar(value=self.config.show_tooltips)
        ttk.Checkbutton(ui_frame, text="Show tooltips",
                       variable=self.tooltips_var).pack(anchor=tk.W, padx=5, pady=5)
        
        self.confirm_var = tk.BooleanVar(value=self.config.confirm_deletions)
        ttk.Checkbutton(ui_frame, text="Confirm deletions",
                       variable=self.confirm_var).pack(anchor=tk.W, padx=5, pady=5)
        
        self.enhanced_var = tk.BooleanVar(value=self.config.enhanced_mode_default)
        ttk.Checkbutton(ui_frame, text="Use enhanced mode by default",
                       variable=self.enhanced_var).pack(anchor=tk.W, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Apply", command=self.apply_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="OK", command=self.ok_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Reset to Defaults", command=self.reset_defaults).pack(side=tk.RIGHT, padx=5)
    
    def apply_settings(self):
        """Apply settings without closing dialog"""
        self.config.theme = self.theme_var.get()
        self.config.font_family = self.font_family_var.get()
        self.config.font_size = self.font_size_var.get()
        self.config.auto_save_enabled = self.auto_save_var.get()
        self.config.auto_save_interval = self.interval_var.get()
        self.config.search_fuzzy_threshold = self.fuzzy_var.get()
        self.config.search_case_sensitive = self.case_var.get()
        
        # Performance settings
        self.config.use_search_indexing = self.indexing_var.get()
        self.config.use_lazy_loading = self.lazy_loading_var.get()
        self.config.lazy_loading_threshold = self.threshold_var.get()
        self.config.default_page_size = self.page_size_var.get()
        self.config.search_debounce_delay = self.debounce_var.get()
        self.config.background_processing = self.background_var.get()
        self.config.show_performance_monitor = self.perf_monitor_var.get()
        
        # UI preferences
        self.config.show_tooltips = self.tooltips_var.get()
        self.config.confirm_deletions = self.confirm_var.get()
        self.config.enhanced_mode_default = self.enhanced_var.get()
        
        self.config_manager.save_config()
    
    def ok_settings(self):
        """Apply settings and close dialog"""
        self.apply_settings()
        self.dialog.destroy()
    
    def reset_defaults(self):
        """Reset all settings to defaults"""
        self.config_manager.config = AppConfig()
        self.config_manager.save_config()
        self.dialog.destroy()