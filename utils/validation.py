import re
from urllib.parse import urlparse

def validate_url(url):
    """
    Validate a URL using regex pattern matching.
    
    Args:
        url (str): The URL to validate
        
    Returns:
        bool: True if the URL is valid, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    # URL pattern for validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None

def normalize_url(url):
    """
    Normalize a URL by adding https:// prefix if missing.
    
    Args:
        url (str): The URL to normalize
        
    Returns:
        str: The normalized URL
    """
    if not url:
        return url
    
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    return url

def is_valid_domain(url):
    """
    Check if a URL has a valid domain structure.
    
    Args:
        url (str): The URL to check
        
    Returns:
        bool: True if domain is valid, False otherwise
    """
    try:
        parsed = urlparse(url)
        return bool(parsed.netloc)
    except:
        return False

def validate_and_normalize_url(url):
    """
    Validate and normalize a URL.
    
    Args:
        url (str): The URL to validate and normalize
        
    Returns:
        tuple: (is_valid, normalized_url, error_message)
    """
    if not url or not isinstance(url, str):
        return False, url, "URL cannot be empty"
    
    # Normalize the URL
    normalized = normalize_url(url)
    
    # Validate the normalized URL
    if not validate_url(normalized):
        return False, normalized, "Invalid URL format"
    
    # Check domain validity
    if not is_valid_domain(normalized):
        return False, normalized, "Invalid domain"
    
    return True, normalized, None 