"""Custom exceptions for NCBI searches"""

class NCBISearchError(Exception):
    """Base exception for all NCBI search errors"""
    pass

class RateLimitError(NCBISearchError):
    """Raised when NCBI rate limit is exceeded"""
    pass

class InvalidSearchTermError(NCBISearchError):
    """Raised when invalid search terms are provided"""
    pass

class AuthenticationError(NCBISearchError):
    """Raised when authentication fails"""
    pass
