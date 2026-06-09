from fastapi import APIRouter, Depends, Query
from app.models.response import APIResponse
from app.models.professor import Professor
from app.services.university_scraper import UniversityProfileScraper
from app.core.logging import get_logger
from app.core.config import Settings, get_settings
import os

router = APIRouter()
logger = get_logger(__name__)

@router.get("/health", response_model=APIResponse[dict[str, str]], tags=["System"])
async def health_check(
    settings: Settings = Depends(get_settings)
) -> APIResponse[dict[str, str]]:
    """
    Enhanced health check to verify service and storage status.
    """
    logger.debug("Health check requested")
    data_dir_ok = os.path.exists(settings.DATA_DIR)
    return APIResponse(
        success=True,
        data={
            "status": "healthy",
            "version": "0.1.0",
            "storage_ok": str(data_dir_ok)
        },
        message="Service is operational"
    )
