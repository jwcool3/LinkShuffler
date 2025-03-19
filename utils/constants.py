# Application constants

# Version
APP_VERSION = "2.0.0"
APP_NAME = "Bookmark Manager"

# UI constants
DEFAULT_WINDOW_SIZE = "1000x700"
MIN_WINDOW_SIZE = (800, 600)

# Default values
DEFAULT_PAGE_SIZE = 25
MAX_SHUFFLE_COUNT = 100
MIN_SHUFFLE_COUNT = 1
DEFAULT_SHUFFLE_COUNT = 5

# Minimum rating
MIN_RATING = 1
MAX_RATING = 5

# Category constants
UNCATEGORIZED = "Uncategorized"
DEFAULT_CATEGORIES = [UNCATEGORIZED]

# Stop words for keyword extraction
STOP_WORDS = {
    'a', 'an', 'the', 'and', 'or', 'but', 'is', 'are', 'on', 'in', 'to', 'for',
    'with', 'by', 'at', 'from', 'of', 'this', 'that', 'these', 'those', 'it',
    'its', 'his', 'her', 'their', 'our', 'your', 'has', 'have', 'had', 'was',
    'were', 'be', 'been', 'being', 'do', 'does', 'did', 'will', 'would', 'shall',
    'should', 'can', 'could', 'may', 'might', 'must', 'com', 'net', 'org', 'www'
}

# Minimum keyword length
MIN_KEYWORD_LENGTH = 3

# TF-IDF thresholds
TFIDF_THRESHOLD = 0.1
MIN_DOCUMENT_FREQUENCY = 2
MAX_DOCUMENT_FREQUENCY = 0.8