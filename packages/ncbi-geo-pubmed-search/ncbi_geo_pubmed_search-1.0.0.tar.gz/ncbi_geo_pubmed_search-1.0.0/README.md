# ncbi-geo-pubmed-search

[![PyPI version](https://badge.fury.io/py/ncbi-geo-pubmed-search.svg)](https://badge.fury.io/py/ncbi-geo-pubmed-search)
[![Python](https://img.shields.io/pypi/pyversions/ncbi-geo-pubmed-search.svg)](https://pypi.org/project/ncbi-geo-pubmed-search/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful Python package for searching NCBI GEO and PubMed databases with advanced filtering

## Features

- 🔍 **Unified Search Interface**: Search both PubMed and GEO databases with a single command
- 🏥 **PubMed Search**: Find scientific articles with advanced filtering by date, field, and more
- 🧬 **GEO Search**: Discover gene expression datasets with organism and dataset type filtering
- 🛡️ **Robust Error Handling**: Built-in retry logic with exponential backoff for API rate limits
- 📊 **Flexible Output**: Export results to Excel or CSV formats
- 🔧 **Highly Configurable**: Customize API delays, retries, and search parameters
- 🌍 **Environment Variable Support**: Secure credential management
- 📈 **Result Statistics**: Get summary statistics for your search results

## Installation

Install from PyPI:

```bash
pip install ncbi-geo-pubmed-search
```

Or install the latest development version:

```bash
pip install git+https://github.com/yourusername/ncbi-geo-pubmed-search.git
```

## Quick Start

### Basic Usage

```python
from ncbi_geo_pubmed import NCBISearcher

# Initialize with your email (required by NCBI)
searcher = NCBISearcher(email="your.email@example.com")

# Search both PubMed and GEO
results = searcher.search(
    search_terms=["cancer", "immunotherapy"],
    start_year=2020,
    end_year=2024
)

# Access results
pubmed_df = results["pubmed"]
geo_df = results["geo_all"]

print(f"Found {len(pubmed_df)} PubMed articles")
print(f"Found {len(geo_df)} GEO datasets")
```

### Using Environment Variables

Set your credentials as environment variables for security:

```bash
export NCBI_EMAIL="your.email@example.com"
export NCBI_API_KEY="your_optional_api_key"
```

Then use without explicit credentials:

```python
from ncbi_geo_pubmed import NCBISearcher

searcher = NCBISearcher()
results = searcher.search(["aging", "senescence"], 2022, 2024)
```

### Search Only PubMed

```python
# Search PubMed with specific field
pubmed_results = searcher.search_pubmed(
    search_terms=["CRISPR", "gene editing"],
    start_year=2023,
    end_year=2024,
    field="Title/Abstract",  # Search in title and abstract
    retmax=500
)

# Save results
pubmed_results = searcher.search_pubmed(
    search_terms=["diabetes", "metabolism"],
    start_year=2020,
    end_year=2024,
    output_folder="./results",
    save_format="excel"
)
```

### Search Only GEO

```python
# Search GEO with organism filter
geo_results = searcher.search_geo(
    search_terms=["RNA-seq", "single cell"],
    organisms=["Homo sapiens", "Mus musculus"],
    dataset_type="expression profiling by high throughput sequencing",
    retmax=1000
)

# Access organism-specific results
human_datasets = geo_results["geo_homo_sapiens"]
mouse_datasets = geo_results["geo_mus_musculus"]
```

## Advanced Usage

### Custom Configuration

```python
# Initialize with custom settings
searcher = NCBISearcher(
    email="your.email@example.com",
    api_key="your_api_key",  # Optional, provides higher rate limits
    request_delay=0.5,       # Delay between requests (seconds)
    max_retries=5,          # Maximum retry attempts
    backoff_factor=2        # Exponential backoff multiplier
)
```

### Combined Search with All Options

```python
results = searcher.search(
    search_terms=["alzheimer", "neurodegeneration", "tau"],
    start_year=2020,
    end_year=2024,
    databases=["pubmed", "geo"],  # Which databases to search
    organisms=["Homo sapiens"],    # GEO organism filter
    retmax=2000,                   # Max results per database
    pubmed_field="Title/Abstract", # PubMed search field
    geo_dataset_type="expression profiling by array",
    output_folder="./alzheimer_results",
    save_format="excel",
    combine_results=True  # Save all results in one file
)

# Get summary statistics
stats = searcher.get_stats(results)
print(stats)
```

### Batch Processing

```python
# Process multiple search topics
topics = [
    {"terms": ["COVID-19", "long COVID"], "years": (2021, 2024)},
    {"terms": ["cancer", "immunotherapy"], "years": (2022, 2024)},
    {"terms": ["CRISPR", "base editing"], "years": (2020, 2024)}
]

all_results = {}
for topic in topics:
    key = "_".join(topic["terms"])
    results = searcher.search(
        search_terms=topic["terms"],
        start_year=topic["years"][0],
        end_year=topic["years"][1],
        retmax=100
    )
    all_results[key] = results
```

## Output Examples

### PubMed Results DataFrame

| PMID | Title | Authors | Journal | Year | DOI | Citation |
|------|-------|---------|---------|------|-----|----------|
| 12345678 | Cancer immunotherapy... | Smith J, et al. | Nature | 2023 | 10.1038/... | Nature. 123(45):678-90 (2023) |

### GEO Results DataFrame

| GEO_ID | Accession | Title | Organism | Platform | Samples | DatasetType |
|--------|-----------|-------|----------|----------|---------|-------------|
| 200012345 | GSE12345 | Single-cell RNA-seq... | Homo sapiens | GPL20301 | 10000 | expression profiling... |

## Error Handling

The package includes robust error handling:

```python
from ncbi_geo_pubmed import NCBISearcher, NCBISearchError, RateLimitError

try:
    searcher = NCBISearcher(email="your.email@example.com")
    results = searcher.search(["cancer"], 2020, 2024)
except RateLimitError:
    print("Rate limit exceeded. Try again later or use an API key.")
except NCBISearchError as e:
    print(f"Search failed: {e}")
```

## Command Line Interface (CLI)

The package also provides a command-line interface:

```bash
# Basic search
ncbi-search --email your.email@example.com --terms "cancer,immunotherapy" --start 2020 --end 2024

# Search with all options
ncbi-search \
    --email your.email@example.com \
    --api-key your_api_key \
    --terms "aging,senescence" \
    --start 2020 \
    --end 2024 \
    --databases pubmed geo \
    --organisms "Homo sapiens" "Mus musculus" \
    --output ./results \
    --format excel
```

## Requirements

- Python >= 3.7
- biopython >= 1.79
- pandas >= 1.3.0
- openpyxl >= 3.0.9
- requests >= 2.25.0

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

If you encounter any problems or have questions:

1. Check the [FAQ](https://github.com/yourusername/ncbi-geo-pubmed-search/wiki/FAQ)
2. Look through [existing issues](https://github.com/yourusername/ncbi-geo-pubmed-search/issues)
3. Open a new issue with a detailed description

## Citation

If you use this package in your research, please cite:

```bibtex
@software{ncbi-geo-pubmed-search,
  author = {{ Your Name }},
  title = {{ ncbi-geo-pubmed-search: A powerful Python package for searching NCBI GEO and PubMed databases with advanced filtering }},
  year = {2024},
  url = {https://github.com/yourusername/ncbi-geo-pubmed-search}
}
```

## Acknowledgments

- NCBI for providing the E-utilities API
- The BioPython community for the excellent Bio.Entrez module
- All contributors and users of this package

---

Made with ❤️ for the bioinformatics community
