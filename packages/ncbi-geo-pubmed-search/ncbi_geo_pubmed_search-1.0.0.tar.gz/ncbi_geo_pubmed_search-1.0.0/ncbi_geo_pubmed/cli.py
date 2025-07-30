"""Command-line interface for ncbi-geo-pubmed package"""

import argparse
import sys
import os
from typing import List
import logging

from .core import NCBISearcher
from . import __version__


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Search NCBI PubMed and GEO databases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic PubMed search
  ncbi-search --email user@example.com --terms "cancer,immunotherapy" --start 2020 --end 2024

  # Search both databases with output
  ncbi-search --email user@example.com --terms "COVID-19" --start 2020 --end 2024 \
              --databases pubmed geo --output ./results --format excel

  # GEO search with organism filter  
  ncbi-search --email user@example.com --terms "RNA-seq" --databases geo \
              --organisms "Homo sapiens" "Mus musculus" --output ./geo_data
        """
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"%(prog)s {__version__}"
    )
    
    # Required arguments
    parser.add_argument(
        "--email",
        required=True,
        help="Email address (required by NCBI)"
    )
    
    parser.add_argument(
        "--terms",
        required=True,
        help="Search terms separated by commas"
    )
    
    # Optional arguments
    parser.add_argument(
        "--api-key",
        help="NCBI API key for higher rate limits"
    )
    
    parser.add_argument(
        "--start",
        type=int,
        default=2020,
        help="Start year for PubMed search (default: 2020)"
    )
    
    parser.add_argument(
        "--end",
        type=int,
        default=2024,
        help="End year for PubMed search (default: 2024)"
    )
    
    parser.add_argument(
        "--databases",
        nargs="+",
        choices=["pubmed", "geo"],
        default=["pubmed", "geo"],
        help="Databases to search (default: both)"
    )
    
    parser.add_argument(
        "--organisms",
        nargs="+",
        default=["Homo sapiens", "Mus musculus"],
        help="Organisms for GEO search"
    )
    
    parser.add_argument(
        "--max-results",
        type=int,
        default=1000,
        help="Maximum results per database (default: 1000)"
    )
    
    parser.add_argument(
        "--output",
        help="Output directory for results"
    )
    
    parser.add_argument(
        "--format",
        choices=["excel", "csv"],
        default="excel",
        help="Output format (default: excel)"
    )
    
    parser.add_argument(
        "--combine",
        action="store_true",
        help="Combine all results into one file"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser.parse_args()


def main():
    """Main CLI entry point"""
    args = parse_args()
    
    # Set up logging
    level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Parse search terms
    search_terms = [term.strip() for term in args.terms.split(",")]
    
    try:
        # Initialize searcher
        searcher = NCBISearcher(
            email=args.email,
            api_key=args.api_key
        )
        
        # Perform search
        print(f"Searching {', '.join(args.databases)} for: {', '.join(search_terms)}")
        
        results = searcher.search(
            search_terms=search_terms,
            start_year=args.start,
            end_year=args.end,
            databases=args.databases,
            organisms=args.organisms,
            retmax=args.max_results,
            output_folder=args.output,
            save_format=args.format,
            combine_results=args.combine
        )
        
        # Print summary
        print("\nSearch Results:")
        for db_name, df in results.items():
            if not df.empty:
                print(f"  {db_name}: {len(df)} results")
        
        if args.output:
            print(f"\nResults saved to: {args.output}")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
