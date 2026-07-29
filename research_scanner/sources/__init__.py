"""
Data source modules for research_scanner (arXiv, USPTO, Currents API).
"""

from research_scanner.sources.arxiv import fetch_arxiv_items
from research_scanner.sources.uspto import fetch_uspto_items
from research_scanner.sources.currents import fetch_currents_items

__all__ = ["fetch_arxiv_items", "fetch_uspto_items", "fetch_currents_items"]
