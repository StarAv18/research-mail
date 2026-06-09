from fastapi import APIRouter, Depends, Query
from app.models.response import APIResponse
from app.models.professor import Professor
from app.services.university_scraper import UniversityProfileScraper
from app.api.deps import get_scraper_service

router = APIRouter()

@router.get("/scrape", response_model=APIResponse[Professor])
async def scrape_professor(
    url: str = Query(..., description="University profile URL"),
    scraper: UniversityProfileScraper = Depends(get_scraper_service)
) -> APIResponse[Professor]:
    """Scrape a professor profile from a university URL."""
    professor = scraper.scrape(url)
    return APIResponse(success=True, data=professor, message="Professor profile extracted successfully")
