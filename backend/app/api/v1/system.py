from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.models.response import APIResponse
from app.models.professor import Professor
from app.models.draft import DraftStatus
from app.models.db_models import ProfessorDB, DraftDB
from app.core.db import get_db
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

@router.get("/metrics", response_model=APIResponse[dict[str, int]])
async def metrics(db: Session = Depends(get_db)) -> APIResponse[dict[str, int]]:
    """Dashboard metrics backed by the database."""
    return APIResponse(
        success=True,
        data={
            "professors_found": db.query(ProfessorDB).count(),
            "drafts_created": db.query(DraftDB).count(),
            "emails_sent": db.query(DraftDB).filter(DraftDB.status == DraftStatus.SENT).count(),
            "response_rate": 0,
        },
    )
