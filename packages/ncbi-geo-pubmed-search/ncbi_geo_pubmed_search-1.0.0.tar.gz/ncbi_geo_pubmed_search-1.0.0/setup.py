"""Setup configuration for ncbi-geo-pubmed-search package"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="ncbi-geo-pubmed-search",
    version="1.0.0",
    author="MD BABU MIA, PHD",
    author_email="md.babu.mia@mssm.edu",
    description="A powerful Python package for searching NCBI GEO and PubMed databases with advanced filtering",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mdbabumiamssm/ncbi-geo-pubmed-search",
    project_urls={
        "Bug Tracker": "https://github.com/mdbabumiamssm/ncbi-geo-pubmed-search/issues",
        "Documentation": "https://github.com/mdbabumiamssm/ncbi-geo-pubmed-search#readme",
        "Source Code": "https://github.com/mdbabumiamssm/ncbi-geo-pubmed-search",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "biopython>=1.79",
        "pandas>=1.3.0",
        "openpyxl>=3.0.9",
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.910",
            "sphinx>=4.0",
            "twine>=3.0",
            "wheel>=0.36",
        ],
    },
    entry_points={
        "console_scripts": [
            "ncbi-search=ncbi_geo_pubmed.cli:main",
        ],
    },
    keywords=[
        "ncbi", "pubmed", "geo", "bioinformatics", "genomics",
        "gene expression", "scientific literature", "data mining",
        "biomedical research", "api wrapper"
    ],
)
