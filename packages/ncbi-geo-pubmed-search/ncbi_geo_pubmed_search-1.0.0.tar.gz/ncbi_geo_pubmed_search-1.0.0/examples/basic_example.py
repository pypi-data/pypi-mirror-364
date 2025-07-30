"""
Basic example of using ncbi-geo-pubmed package
"""

from ncbi_geo_pubmed import NCBISearcher

def main():
    # Initialize searcher
    # You can set email directly or use environment variable NCBI_EMAIL
    searcher = NCBISearcher(email="your.email@example.com")
    
    # Define search parameters
    search_terms = ["cancer", "immunotherapy"]
    start_year = 2022
    end_year = 2024
    
    print(f"Searching for: {', '.join(search_terms)}")
    print(f"Year range: {start_year}-{end_year}")
    print("-" * 50)
    
    # Perform search
    results = searcher.search(
        search_terms=search_terms,
        start_year=start_year,
        end_year=end_year,
        retmax=100  # Limit to 100 results for demo
    )
    
    # Display results summary
    print("\nSearch Results Summary:")
    for db_name, df in results.items():
        print(f"{db_name}: {len(df)} results")
    
    # Show sample PubMed results
    if "pubmed" in results and not results["pubmed"].empty:
        print("\nSample PubMed Articles:")
        print("-" * 50)
        
        for idx, row in results["pubmed"].head(3).iterrows():
            print(f"PMID: {row['PMID']}")
            print(f"Title: {row['Title'][:100]}...")
            print(f"Year: {row['Year']}")
            print(f"Journal: {row['Journal']}")
            print("-" * 50)
    
    # Show sample GEO results
    if "geo_all" in results and not results["geo_all"].empty:
        print("\nSample GEO Datasets:")
        print("-" * 50)
        
        for idx, row in results["geo_all"].head(3).iterrows():
            print(f"GEO ID: {row['GEO_ID']}")
            print(f"Title: {row['Title'][:100]}...")
            print(f"Organism: {row['Organism']}")
            print(f"Samples: {row['Samples']}")
            print("-" * 50)

if __name__ == "__main__":
    main()
