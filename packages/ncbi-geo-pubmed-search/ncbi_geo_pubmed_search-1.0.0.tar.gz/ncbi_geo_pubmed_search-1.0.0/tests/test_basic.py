"""Basic tests for ncbi-geo-pubmed package"""

import pytest
import os
from unittest.mock import Mock, patch

from ncbi_geo_pubmed import NCBISearcher, NCBISearchError, RateLimitError
from ncbi_geo_pubmed.config import SearchConfig
from ncbi_geo_pubmed.utils import validate_search_terms, validate_year_range


class TestConfig:
    """Test configuration"""
    
    def test_config_with_email(self):
        """Test config initialization with email"""
        config = SearchConfig(email="test@example.com")
        assert config.email == "test@example.com"
        assert config.request_delay == 0.10
    
    def test_config_without_email(self):
        """Test config without email raises error"""
        with pytest.raises(ValueError, match="Email is required"):
            SearchConfig()
    
    @patch.dict(os.environ, {"NCBI_EMAIL": "env@example.com"})
    def test_config_from_environment(self):
        """Test config loads from environment"""
        config = SearchConfig()
        assert config.email == "env@example.com"


class TestValidation:
    """Test validation functions"""
    
    def test_validate_search_terms_valid(self):
        """Test valid search terms"""
        validate_search_terms(["cancer", "therapy"])
        # Should not raise
    
    def test_validate_search_terms_empty(self):
        """Test empty search terms"""
        with pytest.raises(ValueError, match="at least one search term"):
            validate_search_terms([])
    
    def test_validate_search_terms_invalid_type(self):
        """Test non-string search terms"""
        with pytest.raises(ValueError, match="must be strings"):
            validate_search_terms(["valid", 123])
    
    def test_validate_year_range_valid(self):
        """Test valid year range"""
        validate_year_range(2020, 2024)
        # Should not raise
    
    def test_validate_year_range_invalid(self):
        """Test invalid year range"""
        with pytest.raises(ValueError, match="Start year must be less"):
            validate_year_range(2024, 2020)


class TestNCBISearcher:
    """Test main searcher class"""
    
    def test_initialization(self):
        """Test searcher initialization"""
        searcher = NCBISearcher(email="test@example.com")
        assert searcher.config.email == "test@example.com"
    
    @patch('ncbi_geo_pubmed.search.PubMedSearcher.search')
    @patch('ncbi_geo_pubmed.search.GEOSearcher.search')
    def test_search_both_databases(self, mock_geo, mock_pubmed):
        """Test searching both databases"""
        # Setup mocks
        mock_pubmed.return_value = [
            {"PMID": "123", "Title": "Test Article"}
        ]
        mock_geo.return_value = (
            [{"GEO_ID": "456", "Title": "Test Dataset"}],
            {"Homo sapiens": [{"GEO_ID": "456", "Title": "Test Dataset"}]}
        )
        
        # Perform search
        searcher = NCBISearcher(email="test@example.com")
        results = searcher.search(
            search_terms=["test"],
            start_year=2020,
            end_year=2024
        )
        
        # Verify
        assert "pubmed" in results
        assert "geo_all" in results
        assert len(results["pubmed"]) == 1
        assert len(results["geo_all"]) == 1


if __name__ == "__main__":
    pytest.main([__file__])
