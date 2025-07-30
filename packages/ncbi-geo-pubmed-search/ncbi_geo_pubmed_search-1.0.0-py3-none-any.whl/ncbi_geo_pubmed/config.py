"""Configuration module for NCBI API settings"""

import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class SearchConfig:
    """Configuration for NCBI searches"""
    email: Optional[str] = None
    api_key: Optional[str] = None
    request_delay: float = 0.10
    max_retries: int = 3
    backoff_factor: int = 2
    
    def __post_init__(self):
        # Try to load from environment variables if not provided
        if not self.email:
            self.email = os.getenv("NCBI_EMAIL")
        if not self.api_key:
            self.api_key = os.getenv("NCBI_API_KEY")
            
        # Validate email is provided
        if not self.email:
            raise ValueError(
                "Email is required by NCBI. Please provide it via parameter "
                "or set NCBI_EMAIL environment variable."
            )
