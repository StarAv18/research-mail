from abc import ABC, abstractmethod
from typing import Optional
from bs4 import BeautifulSoup
from app.models.professor import Professor

class BaseScraper(ABC):
    """
    Abstract base class for all scrapers to ensure consistent interface.
    """
    
    @abstractmethod
    def scrape(self, url: str) -> Professor:
        """
        Scrape the given URL and return a Professor object.
        """
        pass

class BaseHTMLScraper(BaseScraper):
    """
    Common HTML parsing utilities shared across different scraper implementations.
    """
    
    def _clean_text(self, text: str) -> str:
        """Helper to clean and normalize extracted text."""
        return " ".join(text.split()).strip()

    @abstractmethod
    def _extract_name(self, soup: BeautifulSoup) -> Optional[str]:
        pass

    @abstractmethod
    def _extract_email(self, html_content: str) -> Optional[str]:
        pass
