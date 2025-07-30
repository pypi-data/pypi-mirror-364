"""Utility functions for NCBI searches"""

import time
import logging
from typing import Callable, Any, TypeVar, Optional
from urllib.error import HTTPError
from functools import wraps

from .exceptions import RateLimitError

logger = logging.getLogger(__name__)

T = TypeVar('T')

def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: int = 2,
    exceptions: tuple = (HTTPError,)
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for retrying functions with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Factor to multiply delay by after each retry
        exceptions: Tuple of exceptions to catch and retry
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if isinstance(e, HTTPError) and e.code == 429:
                        # Rate limit hit
                        delay = initial_delay * (backoff_factor ** attempt)
                        logger.warning(
                            f"Rate limited (HTTP 429). Retrying in {delay:.1f}s "
                            f"(attempt {attempt + 1}/{max_retries})"
                        )
                        
                        if attempt == max_retries - 1:
                            raise RateLimitError(
                                f"Rate limit exceeded after {max_retries} attempts"
                            ) from e
                    else:
                        logger.error(f"Error in {func.__name__}: {e}")
                        
                        if attempt == max_retries - 1:
                            raise
                    
                    # Calculate delay
                    delay = initial_delay * (backoff_factor ** attempt)
                    time.sleep(delay)
            
            # Should not reach here, but just in case
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator

def validate_search_terms(terms: list) -> None:
    """Validate search terms"""
    if not terms:
        raise ValueError("At least one search term is required")
    
    if not all(isinstance(term, str) for term in terms):
        raise ValueError("All search terms must be strings")
    
    if not all(term.strip() for term in terms):
        raise ValueError("Search terms cannot be empty")

def validate_year_range(start_year: int, end_year: int) -> None:
    """Validate year range"""
    current_year = time.localtime().tm_year
    
    if start_year > end_year:
        raise ValueError("Start year must be less than or equal to end year")
    
    if start_year < 1900:
        raise ValueError("Start year must be 1900 or later")
    
    if end_year > current_year + 1:
        raise ValueError(f"End year cannot be more than {current_year + 1}")

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage"""
    # Replace invalid characters
    invalid_chars = '<>:"|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    
    return filename.strip()
