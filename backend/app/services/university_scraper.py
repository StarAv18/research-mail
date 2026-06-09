import re
import requests
from bs4 import BeautifulSoup
from typing import Optional
from app.models.professor import Professor
from app.core.logging import get_logger
from app.core.exceptions import StarletteHTTPException
from app.services.scraper_base import BaseHTMLScraper

logger = get_logger(__name__)

class UniversityProfileScraper(BaseHTMLScraper):
    """
    Scraper for extracting professor information from university profile pages.
    Refactored for better extraction strategies and robustness.
    """

    def __init__(self, timeout: int = 10, session: Optional[requests.Session] = None):
        self.timeout = timeout
        self.session = session or requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def scrape(self, url: str) -> Professor:
        """
        Scrape a university profile page with enhanced error handling.
        """
        try:
            response = self.session.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
        except requests.Timeout:
            logger.error(f"Timeout reaching URL {url}")
            raise StarletteHTTPException(status_code=408, detail=f"Request to {url} timed out.")
        except requests.RequestException as e:
            logger.error(f"Failed to fetch URL {url}: {str(e)}")
            raise StarletteHTTPException(status_code=400, detail=f"Could not reach the university profile: {str(e)}")

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Priority-based extraction
        name = self._extract_name(soup)
        email = self._extract_email(response.text)
        website = self._extract_website(soup, url)
        research_text = self._extract_research_text(soup)

        return Professor(
            name=name or "Unknown Name",
            university=self._infer_university(url, soup),
            email=email,
            website=website,
            biography=research_text
        )

    def _extract_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Improved name extraction using CSS selectors and metadata."""
        # Try metadata first
        meta_name = soup.find("meta", property="og:title")
        if meta_name and meta_name.get("content"):
            return self._clean_text(meta_name["content"].split("|")[0])

        # Common profile selectors
        selectors = [
            "h1.profile-name", "h1.name", ".professor-name", 
            "h1", "h2.name", ".faculty-name"
        ]
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return self._clean_text(element.get_text())
        
        return None

    def _extract_email(self, html_content: str) -> Optional[str]:
        """Robust email extraction with obfuscation handling (simple cases)."""
        # Basic regex
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(email_pattern, html_content)
        if match:
            return match.group(0).lower()
        
        # Handle common obfuscation: "name (at) univ (dot) edu"
        obfuscated = re.search(r'([a-zA-Z0-9._%+-]+)\s*[\(\[]at[\)\]]\s*([a-zA-Z0-9.-]+)\s*[\(\[]dot[\)\]]\s*([a-zA-Z]{2,})', html_content, re.I)
        if obfuscated:
            return f"{obfuscated.group(1)}@{obfuscated.group(2)}.{obfuscated.group(3)}".lower()
            
        return None

    def _extract_website(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Heuristic-based website extraction."""
        keywords = ["personal", "lab", "research", "group", "homepage", "cv", "website"]
        for a in soup.find_all("a", href=True):
            text = a.get_text().lower()
            href = a['href'].lower()
            # Avoid generic university links
            if any(k in text or k in href for k in keywords):
                if any(k in href for k in ["facebook", "twitter", "linkedin", "google-scholar"]):
                    continue
                target = a['href']
                if target.startswith("/"):
                    from urllib.parse import urljoin
                    return urljoin(base_url, target)
                return target
        return base_url

    def _extract_research_text(self, soup: BeautifulSoup) -> str:
        """Section-based extraction for research interests."""
        research_keywords = ["research", "interests", "biography", "about", "publications"]
        found_text = []

        # Strategy 1: Look for semantic sections
        for section in soup.find_all(["section", "div", "article"]):
            header = section.find(["h1", "h2", "h3", "h4"])
            if header and any(k in header.get_text().lower() for k in research_keywords):
                # Clean header text from the content
                content = section.get_text(separator=" ", strip=True)
                found_text.append(content)

        # Strategy 2: Look for headers and their siblings (if Strategy 1 found nothing)
        if not found_text:
            for header in soup.find_all(["h1", "h2", "h3", "h4"]):
                if any(k in header.get_text().lower() for k in research_keywords):
                    section_content = []
                    for sibling in header.find_next_siblings():
                        if sibling.name in ["h1", "h2", "h3", "h4"]:
                            break
                        section_content.append(sibling.get_text(separator=" ", strip=True))
                    if section_content:
                        found_text.append(" ".join(section_content))

        if not found_text:
            # Fallback to paragraph-based strategy
            paragraphs = soup.find_all("p")
            found_text = [p.get_text(strip=True) for p in paragraphs if len(p.get_text()) > 50]

        return self._clean_text("\n\n".join(found_text))[:5000]

    def _infer_university(self, url: str, soup: BeautifulSoup) -> str:
        """Infer university name from URL or metadata."""
        domain_match = re.search(r'https?://(?:www\.)?([a-zA-Z0-9.-]+)\.edu', url)
        if domain_match:
            return domain_match.group(1).replace("-", " ").title()
        
        meta_site = soup.find("meta", property="og:site_name")
        if meta_site:
            return meta_site.get("content", "Unknown University")
            
        return "Unknown University"
