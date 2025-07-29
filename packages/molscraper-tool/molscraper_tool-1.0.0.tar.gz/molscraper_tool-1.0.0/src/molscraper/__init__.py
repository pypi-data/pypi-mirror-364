"""
Molscraper - Chemical data extraction tool for researchers and chemists.

Extract detailed chemical compound information from PubChem's REST API.
"""

__version__ = "1.0.0"
__author__ = "Xhuliano Brace, Timothy Chia"
__email__ = "x@rhizome-research.com, tim@rhizome-research.com"

# Import main functions for easy access
from .scraper import PubChemScraper, process_compounds_to_csv, CompoundData

# Make main functions available at package level
__all__ = [
    'PubChemScraper',
    'process_compounds_to_csv', 
    'CompoundData',
    '__version__',
    '__author__',
    '__email__'
]
