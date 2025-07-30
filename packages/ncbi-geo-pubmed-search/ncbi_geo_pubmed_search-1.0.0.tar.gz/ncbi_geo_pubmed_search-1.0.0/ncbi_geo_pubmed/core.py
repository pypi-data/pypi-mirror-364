"""
Core module for NCBI GEO & PubMed searches
Main interface for users
"""

import os
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Union, Tuple

import pandas as pd

from .config import SearchConfig
from .search import PubMedSearcher, GEOSearcher
from .utils import validate_search_terms, validate_year_range, sanitize_filename
from .exceptions import NCBISearchError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NCBISearcher:
    """
    Main class for searching NCBI PubMed and GEO databases
    
    This class provides a unified interface for searching both PubMed articles
    and GEO datasets with advanced filtering options.
    
    Examples:
        Basic usage with direct credentials:
        >>> searcher = NCBISearcher(email="your.email@example.com")
        >>> results = searcher.search(["cancer", "immunotherapy"], 2020, 2024)
        
        Using environment variables:
        >>> os.environ['NCBI_EMAIL'] = "your.email@example.com"
        >>> os.environ['NCBI_API_KEY'] = "your_api_key"
        >>> searcher = NCBISearcher()
        
        Advanced search with custom parameters:
        >>> searcher = NCBISearcher(
        ...     email="your.email@example.com",
        ...     api_key="your_api_key",
        ...     request_delay=0.5
        ... )
        >>> results = searcher.search(
        ...     search_terms=["aging", "senescence"],
        ...     start_year=2022,
        ...     end_year=2024,
        ...     databases=["pubmed", "geo"],
        ...     organisms=["Homo sapiens", "Mus musculus"],
        ...     retmax=500,
        ...     output_folder="./results"
        ... )
    """
    
    def __init__(
        self,
        email: Optional[str] = None,
        api_key: Optional[str] = None,
        request_delay: float = 0.10,
        max_retries: int = 3,
        backoff_factor: int = 2
    ):
        """
        Initialize NCBI Searcher
        
        Args:
            email: Email address (required by NCBI). Can also be set via
                   NCBI_EMAIL environment variable
            api_key: NCBI API key for higher rate limits. Can also be set
                    via NCBI_API_KEY environment variable
            request_delay: Delay between API requests in seconds (default: 0.1)
            max_retries: Maximum number of retry attempts for failed requests
            backoff_factor: Exponential backoff factor for retries
            
        Raises:
            ValueError: If email is not provided
        """
        self.config = SearchConfig(
            email=email,
            api_key=api_key,
            request_delay=request_delay,
            max_retries=max_retries,
            backoff_factor=backoff_factor
        )
        
        self.pubmed_searcher = PubMedSearcher(self.config)
        self.geo_searcher = GEOSearcher(self.config)
        
        logger.info(f"NCBISearcher initialized with email: {self.config.email}")
        if self.config.api_key:
            logger.info("API key provided - higher rate limits available")
    
    def search(
        self,
        search_terms: List[str],
        start_year: int,
        end_year: int,
        databases: Optional[List[str]] = None,
        organisms: Optional[List[str]] = None,
        retmax: int = 1000,
        pubmed_field: str = "Title",
        geo_dataset_type: Optional[str] = None,
        output_folder: Optional[Union[str, Path]] = None,
        save_format: str = "excel",
        combine_results: bool = False
    ) -> Dict[str, pd.DataFrame]:
        """
        Search NCBI databases with specified parameters
        
        Args:
            search_terms: List of search terms (e.g., ["cancer", "immunotherapy"])
            start_year: Start year for PubMed date range
            end_year: End year for PubMed date range
            databases: Databases to search. Options: ["pubmed", "geo"]
                      Default: ["pubmed", "geo"]
            organisms: List of organisms for GEO filtering
                      Default: ["Homo sapiens", "Mus musculus"]
            retmax: Maximum number of results per database (default: 1000)
            pubmed_field: PubMed field to search ("Title", "Abstract", "All")
            geo_dataset_type: GEO dataset type filter (e.g., "expression profiling by array")
            output_folder: Folder to save results. If None, results are not saved
            save_format: Format for saving ("excel" or "csv")
            combine_results: If True, combine all results into a single file
            
        Returns:
            Dictionary of pandas DataFrames:
            - "pubmed": PubMed results
            - "geo_all": All GEO results
            - "geo_homo_sapiens": Human GEO datasets
            - "geo_mus_musculus": Mouse GEO datasets
            - etc.
            
        Raises:
            ValueError: If invalid parameters are provided
            NCBISearchError: If search fails
        """
        # Validate inputs
        validate_search_terms(search_terms)
        validate_year_range(start_year, end_year)
        
        if databases is None:
            databases = ["pubmed", "geo"]
        
        # Validate databases
        valid_databases = {"pubmed", "geo"}
        invalid = set(databases) - valid_databases
        if invalid:
            raise ValueError(f"Invalid databases: {invalid}. Valid options: {valid_databases}")
        
        results = {}
        
        # Search PubMed
        if "pubmed" in databases:
            logger.info("Starting PubMed search...")
            try:
                pubmed_results = self.pubmed_searcher.search(
                    search_terms=search_terms,
                    start_year=start_year,
                    end_year=end_year,
                    retmax=retmax,
                    field=pubmed_field
                )
                results["pubmed"] = pd.DataFrame(pubmed_results)
                logger.info(f"PubMed search completed: {len(pubmed_results)} articles found")
            except Exception as e:
                logger.error(f"PubMed search failed: {e}")
                if len(databases) == 1:
                    raise
                results["pubmed"] = pd.DataFrame()
        
        # Search GEO
        if "geo" in databases:
            logger.info("Starting GEO search...")
            try:
                all_datasets, datasets_by_organism = self.geo_searcher.search(
                    search_terms=search_terms,
                    organisms=organisms,
                    retmax=retmax,
                    dataset_type=geo_dataset_type
                )
                
                results["geo_all"] = pd.DataFrame(all_datasets)
                logger.info(f"GEO search completed: {len(all_datasets)} datasets found")
                
                # Add organism-specific results
                for organism, datasets in datasets_by_organism.items():
                    key = f"geo_{organism.lower().replace(' ', '_')}"
                    results[key] = pd.DataFrame(datasets)
                    logger.info(f"  - {organism}: {len(datasets)} datasets")
                    
            except Exception as e:
                logger.error(f"GEO search failed: {e}")
                if len(databases) == 1:
                    raise
                results["geo_all"] = pd.DataFrame()
        
        # Save results if requested
        if output_folder:
            self._save_results(
                results=results,
                output_folder=output_folder,
                search_terms=search_terms,
                save_format=save_format,
                combine_results=combine_results
            )
        
        return results
    
    def search_pubmed(
        self,
        search_terms: List[str],
        start_year: int,
        end_year: int,
        retmax: int = 1000,
        field: str = "Title",
        output_folder: Optional[Union[str, Path]] = None,
        save_format: str = "excel"
    ) -> pd.DataFrame:
        """
        Search only PubMed
        
        Convenience method for searching PubMed without GEO.
        
        Args:
            search_terms: List of search terms
            start_year: Start year for publication date
            end_year: End year for publication date
            retmax: Maximum number of results
            field: Field to search ("Title", "Abstract", "All")
            output_folder: Optional folder to save results
            save_format: Format for saving ("excel" or "csv")
            
        Returns:
            DataFrame with PubMed results
        """
        results = self.search(
            search_terms=search_terms,
            start_year=start_year,
            end_year=end_year,
            databases=["pubmed"],
            retmax=retmax,
            pubmed_field=field,
            output_folder=output_folder,
            save_format=save_format
        )
        
        return results.get("pubmed", pd.DataFrame())
    
    def search_geo(
        self,
        search_terms: List[str],
        organisms: Optional[List[str]] = None,
        retmax: int = 1000,
        dataset_type: Optional[str] = None,
        output_folder: Optional[Union[str, Path]] = None,
        save_format: str = "excel"
    ) -> Dict[str, pd.DataFrame]:
        """
        Search only GEO
        
        Convenience method for searching GEO without PubMed.
        
        Args:
            search_terms: List of search terms
            organisms: List of organisms to filter by
            retmax: Maximum number of results
            dataset_type: Type of dataset to filter
            output_folder: Optional folder to save results
            save_format: Format for saving ("excel" or "csv")
            
        Returns:
            Dictionary of DataFrames with GEO results
        """
        # Use dummy years for PubMed (won't be used)
        current_year = datetime.now().year
        
        results = self.search(
            search_terms=search_terms,
            start_year=current_year,
            end_year=current_year,
            databases=["geo"],
            organisms=organisms,
            retmax=retmax,
            geo_dataset_type=dataset_type,
            output_folder=output_folder,
            save_format=save_format
        )
        
        # Remove pubmed key if present
        results.pop("pubmed", None)
        
        return results
    
    def _save_results(
        self,
        results: Dict[str, pd.DataFrame],
        output_folder: Union[str, Path],
        search_terms: List[str],
        save_format: str,
        combine_results: bool
    ) -> None:
        """Save search results to files"""
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        search_prefix = sanitize_filename("_".join(search_terms[:2]))
        
        if combine_results:
            # Combine all results into one file
            all_data = []
            for db_name, df in results.items():
                if not df.empty:
                    df = df.copy()
                    df["Database"] = db_name
                    all_data.append(df)
            
            if all_data:
                combined_df = pd.concat(all_data, ignore_index=True)
                filename = f"{search_prefix}_combined_{timestamp}"
                
                if save_format == "excel":
                    filepath = output_path / f"{filename}.xlsx"
                    combined_df.to_excel(filepath, index=False)
                else:
                    filepath = output_path / f"{filename}.csv"
                    combined_df.to_csv(filepath, index=False)
                
                logger.info(f"Saved combined results to: {filepath}")
        else:
            # Save separate files
            for db_name, df in results.items():
                if df.empty:
                    continue
                
                filename = f"{search_prefix}_{db_name}_{timestamp}"
                
                if save_format == "excel":
                    filepath = output_path / f"{filename}.xlsx"
                    
                    # For Excel, we can add multiple sheets
                    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                        df.to_excel(writer, sheet_name='Data', index=False)
                        
                        # Add metadata sheet
                        metadata = pd.DataFrame({
                            'Parameter': ['Search Terms', 'Timestamp', 'Total Results'],
                            'Value': [', '.join(search_terms), timestamp, len(df)]
                        })
                        metadata.to_excel(writer, sheet_name='Metadata', index=False)
                else:
                    filepath = output_path / f"{filename}.csv"
                    df.to_csv(filepath, index=False)
                
                logger.info(f"Saved {db_name} results to: {filepath}")
    
    def get_stats(self, results: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Get summary statistics for search results
        
        Args:
            results: Dictionary of search results
            
        Returns:
            DataFrame with summary statistics
        """
        stats = []
        
        for db_name, df in results.items():
            if df.empty:
                continue
            
            stat_row = {
                'Database': db_name,
                'Total_Results': len(df),
                'Columns': ', '.join(df.columns.tolist())
            }
            
            # Add database-specific stats
            if 'pubmed' in db_name:
                if 'Year' in df.columns:
                    year_counts = df['Year'].value_counts()
                    stat_row['Most_Common_Year'] = year_counts.index[0] if len(year_counts) > 0 else 'N/A'
                    stat_row['Year_Range'] = f"{df['Year'].min()} - {df['Year'].max()}" if 'Year' in df.columns else 'N/A'
            
            elif 'geo' in db_name:
                if 'Organism' in df.columns:
                    org_counts = df['Organism'].value_counts()
                    stat_row['Most_Common_Organism'] = org_counts.index[0] if len(org_counts) > 0 else 'N/A'
                if 'DatasetType' in df.columns:
                    type_counts = df['DatasetType'].value_counts()
                    stat_row['Most_Common_Type'] = type_counts.index[0] if len(type_counts) > 0 else 'N/A'
            
            stats.append(stat_row)
        
        return pd.DataFrame(stats)
