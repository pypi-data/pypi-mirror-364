"""
NCBI GEO & PubMed Search Package
A comprehensive tool for searching scientific databases
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core import NCBISearcher
from .exceptions import NCBISearchError, RateLimitError, InvalidSearchTermError

__all__ = [
    "NCBISearcher",
    "NCBISearchError", 
    "RateLimitError",
    "InvalidSearchTermError"
]
