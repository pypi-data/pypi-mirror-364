"""
Advanced example showing all features of ncbi-geo-pubmed package
"""

import os
from ncbi_geo_pubmed import NCBISearcher

def example_with_environment_variables():
    """Example using environment variables for credentials"""
    print("Example 1: Using Environment Variables")
    print("=" * 50)
    
    # Set environment variables (in practice, set these in your shell)
    os.environ['NCBI_EMAIL'] = 'your.email@example.com'
    # os.environ['NCBI_API_KEY'] = 'your_api_key'  # Optional
    
    searcher = NCBISearcher()
    results = searcher.search_pubmed(
        search_terms=["CRISPR", "gene editing"],
        start_year=2023,
        end_year=2024,
        retmax=50
    )
    
    print(f"Found {len(results)} PubMed articles\n")
    return results


def example_geo_with_filters():
    """Example of GEO search with organism and type filters"""
    print("Example 2: GEO Search with Filters")
    print("=" * 50)
    
    searcher = NCBISearcher(email="your.email@example.com")
    
    geo_results = searcher.search_geo(
        search_terms=["single cell", "RNA-seq", "brain"],
        organisms=["Homo sapiens", "Mus musculus", "Rattus norvegicus"],
        dataset_type="expression profiling by high throughput sequencing",
        retmax=200,
        output_folder="./geo_results",
        save_format="excel"
    )
    
    for organism, df in geo_results.items():
        if not df.empty:
            print(f"{organism}: {len(df)} datasets")
    
    print()
    return geo_results


def example_combined_search_with_stats():
    """Example of combined search with statistics"""
    print("Example 3: Combined Search with Statistics")
    print("=" * 50)
    
    searcher = NCBISearcher(
        email="your.email@example.com",
        request_delay=0.2,  # Slower for stability
        max_retries=5       # More retries
    )
    
    # Search both databases
    results = searcher.search(
        search_terms=["alzheimer", "tau protein", "neurodegeneration"],
        start_year=2020,
        end_year=2024,
        databases=["pubmed", "geo"],
        organisms=["Homo sapiens"],
        retmax=500,
        pubmed_field="Title/Abstract",
        output_folder="./alzheimer_study",
        save_format="excel",
        combine_results=False
    )
    
    # Get and display statistics
    stats = searcher.get_stats(results)
    print("\nSearch Statistics:")
    print(stats.to_string())
    
    return results


def example_batch_processing():
    """Example of processing multiple search topics"""
    print("\nExample 4: Batch Processing Multiple Topics")
    print("=" * 50)
    
    searcher = NCBISearcher(email="your.email@example.com")
    
    # Define multiple research topics
    research_topics = [
        {
            "name": "COVID Long Term Effects",
            "terms": ["long COVID", "post-acute COVID", "PASC"],
            "years": (2021, 2024)
        },
        {
            "name": "CAR-T Therapy",
            "terms": ["CAR-T", "chimeric antigen receptor", "immunotherapy"],
            "years": (2022, 2024)
        },
        {
            "name": "Gut Microbiome",
            "terms": ["gut microbiome", "intestinal microbiota", "dysbiosis"],
            "years": (2023, 2024)
        }
    ]
    
    all_results = {}
    
    for topic in research_topics:
        print(f"\nSearching: {topic['name']}")
        print("-" * 30)
        
        results = searcher.search(
            search_terms=topic["terms"],
            start_year=topic["years"][0],
            end_year=topic["years"][1],
            databases=["pubmed"],  # Only PubMed for this example
            retmax=100,
            output_folder=f"./batch_results/{topic['name'].replace(' ', '_')}"
        )
        
        all_results[topic["name"]] = results
        
        # Print summary
        for db_name, df in results.items():
            if not df.empty:
                print(f"  {db_name}: {len(df)} results")
                
                # Show year distribution
                if "Year" in df.columns:
                    year_counts = df["Year"].value_counts().sort_index()
                    print("  Year distribution:")
                    for year, count in year_counts.items():
                        print(f"    {year}: {count}")
    
    return all_results


def example_error_handling():
    """Example showing proper error handling"""
    print("\nExample 5: Error Handling")
    print("=" * 50)
    
    from ncbi_geo_pubmed import NCBISearchError, RateLimitError
    
    try:
        # This will fail without email
        searcher = NCBISearcher()
    except ValueError as e:
        print(f"Expected error: {e}")
    
    try:
        # Proper initialization
        searcher = NCBISearcher(email="your.email@example.com")
        
        # Search with error handling
        results = searcher.search(
            search_terms=["test"],
            start_year=2024,
            end_year=2024,
            retmax=10
        )
        
    except RateLimitError:
        print("Rate limit hit! Consider using an API key or increasing delay")
    except NCBISearchError as e:
        print(f"Search error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def main():
    """Run all examples"""
    print("NCBI GEO & PubMed Search - Advanced Examples")
    print("=" * 70)
    print()
    
    # Note: Replace 'your.email@example.com' with your actual email
    
    # Run examples
    # example_with_environment_variables()
    # example_geo_with_filters()
    # example_combined_search_with_stats()
    # example_batch_processing()
    example_error_handling()
    
    print("\nAll examples completed!")


if __name__ == "__main__":
    main()
