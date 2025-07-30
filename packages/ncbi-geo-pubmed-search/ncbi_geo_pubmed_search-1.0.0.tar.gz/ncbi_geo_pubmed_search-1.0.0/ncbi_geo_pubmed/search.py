"""Search implementations for PubMed and GEO databases"""

import time
import logging
from typing import List, Dict, Optional, Tuple, Any
from abc import ABC, abstractmethod

from Bio import Entrez

from .config import SearchConfig
from .utils import retry_with_backoff, validate_search_terms, validate_year_range
from .exceptions import NCBISearchError

logger = logging.getLogger(__name__)


class BaseSearcher(ABC):
    """Abstract base class for NCBI searchers"""
    
    def __init__(self, config: SearchConfig):
        self.config = config
        Entrez.email = config.email
        if config.api_key:
            Entrez.api_key = config.api_key
    
    @abstractmethod
    def search(self, **kwargs) -> Any:
        """Perform search - must be implemented by subclasses"""
        pass
    
    @retry_with_backoff(max_retries=3)
    def _entrez_search(self, db: str, term: str, retmax: int) -> Dict:
        """Perform Entrez search with retry logic"""
        handle = Entrez.esearch(db=db, term=term, retmax=retmax)
        record = Entrez.read(handle)
        handle.close()
        return record
    
    @retry_with_backoff(max_retries=3)
    def _entrez_summary(self, db: str, id: str) -> Any:
        """Fetch Entrez summary with retry logic"""
        handle = Entrez.esummary(db=db, id=id, retmode="xml")
        summary = Entrez.read(handle)
        handle.close()
        return summary[0] if summary else None


class PubMedSearcher(BaseSearcher):
    """Handles PubMed article searches"""
    
    def search(
        self,
        search_terms: List[str],
        start_year: int,
        end_year: int,
        retmax: int = 1000,
        field: str = "Title"
    ) -> List[Dict[str, str]]:
        """
        Search PubMed for articles
        
        Args:
            search_terms: List of search terms
            start_year: Start year for publication date
            end_year: End year for publication date  
            retmax: Maximum number of results
            field: Field to search in (Title, Abstract, All)
            
        Returns:
            List of article dictionaries
        """
        # Validate inputs
        validate_search_terms(search_terms)
        validate_year_range(start_year, end_year)
        
        # Build query
        term_queries = [f"{term}[{field}]" for term in search_terms]
        date_range = f"{start_year}:{end_year}[PDAT]"
        query = f"({' OR '.join(term_queries)}) AND {date_range}"
        
        logger.info(f"PubMed search query: {query}")
        
        # Search
        results = self._entrez_search("pubmed", query, retmax)
        pmids = results.get("IdList", [])
        
        logger.info(f"Found {len(pmids)} PubMed articles")
        
        # Fetch details
        articles = []
        for i, pmid in enumerate(pmids, 1):
            if i % 100 == 0:
                logger.info(f"Processing PubMed article {i}/{len(pmids)}")
            
            try:
                article = self._fetch_article_details(pmid)
                if article:
                    articles.append(article)
            except Exception as e:
                logger.error(f"Error fetching PMID {pmid}: {e}")
            
            time.sleep(self.config.request_delay)
        
        return articles
    
    def _fetch_article_details(self, pmid: str) -> Optional[Dict[str, str]]:
        """Fetch detailed information for a PubMed article"""
        try:
            summary = self._entrez_summary("pubmed", pmid)
            if not summary:
                return None
            
            # Extract all available fields
            article = {
                "PMID": pmid,
                "Title": summary.get("Title", ""),
                "Authors": self._format_authors(summary.get("AuthorList", [])),
                "Journal": summary.get("Source", ""),
                "PubDate": summary.get("PubDate", ""),
                "Year": self._extract_year(summary.get("PubDate", "")),
                "Volume": summary.get("Volume", ""),
                "Issue": summary.get("Issue", ""),
                "Pages": summary.get("Pages", ""),
                "DOI": summary.get("DOI", ""),
                "Abstract": summary.get("Abstract", ""),
                "Citation": self._build_citation(summary)
            }
            
            return article
            
        except Exception as e:
            logger.error(f"Error processing PMID {pmid}: {e}")
            return None
    
    def _format_authors(self, author_list: List) -> str:
        """Format author list into string"""
        if not author_list:
            return ""
        
        authors = []
        for author in author_list[:5]:  # First 5 authors
            authors.append(author)
        
        if len(author_list) > 5:
            authors.append("et al.")
        
        return ", ".join(authors)
    
    def _extract_year(self, pub_date: str) -> str:
        """Extract year from publication date"""
        if not pub_date:
            return ""
        
        # Try to extract year (first 4 digits)
        import re
        year_match = re.search(r'\d{4}', pub_date)
        return year_match.group() if year_match else ""
    
    def _build_citation(self, summary: Dict) -> str:
        """Build formatted citation"""
        parts = []
        
        # Journal
        if summary.get("Source"):
            parts.append(summary["Source"])
        
        # Volume and issue
        volume = summary.get("Volume", "")
        issue = summary.get("Issue", "")
        if volume:
            if issue:
                parts.append(f"{volume}({issue})")
            else:
                parts.append(volume)
        
        # Pages
        if summary.get("Pages"):
            parts.append(summary["Pages"])
        
        # Year
        year = self._extract_year(summary.get("PubDate", ""))
        if year:
            parts.append(f"({year})")
        
        return ". ".join(parts)


class GEOSearcher(BaseSearcher):
    """Handles GEO dataset searches"""
    
    def search(
        self,
        search_terms: List[str],
        organisms: Optional[List[str]] = None,
        retmax: int = 1000,
        dataset_type: Optional[str] = None
    ) -> Tuple[List[Dict], Dict[str, List[Dict]]]:
        """
        Search GEO for datasets
        
        Args:
            search_terms: List of search terms
            organisms: List of organisms to filter by
            retmax: Maximum number of results
            dataset_type: Type of dataset (e.g., "expression profiling by array")
            
        Returns:
            Tuple of (all_datasets, datasets_by_organism)
        """
        # Validate inputs
        validate_search_terms(search_terms)
        
        if organisms is None:
            organisms = ["Homo sapiens", "Mus musculus"]
        
        # Build query
        term_queries = [f"({term}[Title] OR {term}[Description])" for term in search_terms]
        organism_queries = [f'"{org}"[Organism]' for org in organisms]
        
        query_parts = [f"({' OR '.join(term_queries)})"]
        
        if organisms:
            query_parts.append(f"({' OR '.join(organism_queries)})")
        
        if dataset_type:
            query_parts.append(f'"{dataset_type}"[DataSet Type]')
        
        query = " AND ".join(query_parts)
        
        logger.info(f"GEO search query: {query}")
        
        # Search
        results = self._entrez_search("gds", query, retmax)
        geo_ids = results.get("IdList", [])
        
        logger.info(f"Found {len(geo_ids)} GEO datasets")
        
        # Fetch details
        all_datasets = []
        datasets_by_organism = {org: [] for org in organisms}
        datasets_by_organism["Other"] = []
        
        for i, geo_id in enumerate(geo_ids, 1):
            if i % 50 == 0:
                logger.info(f"Processing GEO dataset {i}/{len(geo_ids)}")
            
            try:
                dataset = self._fetch_dataset_details(geo_id)
                if dataset:
                    all_datasets.append(dataset)
                    
                    # Categorize by organism
                    organism = dataset.get("Organism", "")
                    if organism in datasets_by_organism:
                        datasets_by_organism[organism].append(dataset)
                    else:
                        datasets_by_organism["Other"].append(dataset)
                        
            except Exception as e:
                logger.error(f"Error fetching GEO ID {geo_id}: {e}")
            
            time.sleep(self.config.request_delay)
        
        # Remove empty categories
        datasets_by_organism = {k: v for k, v in datasets_by_organism.items() if v}
        
        return all_datasets, datasets_by_organism
    
    def _fetch_dataset_details(self, geo_id: str) -> Optional[Dict[str, str]]:
        """Fetch detailed information for a GEO dataset"""
        try:
            summary = self._entrez_summary("gds", geo_id)
            if not summary:
                return None
            
            # Extract all available fields
            dataset = {
                "GEO_ID": geo_id,
                "Accession": summary.get("Accession", ""),
                "Title": summary.get("title", ""),
                "Summary": summary.get("summary", ""),
                "Organism": summary.get("taxon", ""),
                "Platform": summary.get("GPL", ""),
                "Samples": str(summary.get("n_samples", "")),
                "DatasetType": summary.get("gdsType", ""),
                "PubMedID": summary.get("PMID", ""),
                "UpdateDate": summary.get("PDAT", ""),
                "Keywords": "; ".join(summary.get("Keywords", [])) if summary.get("Keywords") else ""
            }
            
            return dataset
            
        except Exception as e:
            logger.error(f"Error processing GEO ID {geo_id}: {e}")
            return None
