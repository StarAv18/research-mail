from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Any

class ScraperConfig(BaseModel):
    """Configuration for a scraping task."""
    url: HttpUrl
    depth: int = 1
    timeout: int = 30
    user_agent: str | None = None

class ScrapedData(BaseModel):
    """Model for data extracted from a webpage."""
    url: str
    title: str | None = None
    content: str
    metadata: dict[str, Any] = {}
    scraped_at: datetime = datetime.now()
