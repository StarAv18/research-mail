from datetime import datetime, timedelta
import os
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.models.draft import DraftStatus
from app.models.response import APIResponse
from app.models.db_models import (
    ActivityLogDB,
    DocumentDB,
    EmailCampaignDB,
    EmailDraftDB,
    OutreachStatusDB,
    ProfessorDB,
)
from app.core.db import get_db
from app.core.logging import get_logger
from app.core.config import Settings, get_settings
from app.services.platform_service import build_timeseries

router = APIRouter()
logger = get_logger(__name__)


class AnalyticsSeries(BaseModel):
    daily_outreach: list[dict[str, int | str]]
    weekly_outreach: list[dict[str, int | str]]
    monthly_outreach: list[dict[str, int | str]]
    professors_discovered: int
    drafts_generated: int
    emails_sent: int
    responses_received: int

@router.get("/health", response_model=APIResponse[dict[str, str]], tags=["System"])
async def health_check(
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
) -> APIResponse[dict[str, str]]:
    """
    Enhanced health check to verify service and storage status.
    """
    logger.debug("Health check requested")
    data_dir_ok = os.path.exists(settings.DATA_DIR)
    database_ok = "unknown"
    try:
        db.execute(text("SELECT 1"))
        database_ok = "true"
    except Exception:
        database_ok = "false"
    return APIResponse(
        success=True,
        data={
            "status": "healthy",
            "version": "0.1.0",
            "storage_ok": str(data_dir_ok),
            "database_ok": database_ok,
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
            "drafts_created": db.query(EmailDraftDB).count(),
            "emails_sent": db.query(EmailDraftDB).filter(EmailDraftDB.status == DraftStatus.SENT).count(),
            "responses_received": db.query(OutreachStatusDB).filter(OutreachStatusDB.response_received.is_(True)).count(),
            "campaigns": db.query(EmailCampaignDB).count(),
            "documents": db.query(DocumentDB).count(),
            "activity_events": db.query(ActivityLogDB).count(),
            "response_rate": _response_rate(db),
        },
    )


@router.get("/analytics", response_model=APIResponse[AnalyticsSeries])
async def analytics(db: Session = Depends(get_db)) -> APIResponse[AnalyticsSeries]:
    now = datetime.utcnow()
    daily = _bucket_counts(
        db.query(OutreachStatusDB).filter(OutreachStatusDB.sent_at.is_not(None)).all(),
        "sent_at",
        7,
    )
    weekly = _bucket_counts(
        db.query(OutreachStatusDB).filter(OutreachStatusDB.sent_at >= now - timedelta(days=28)).all(),
        "sent_at",
        28,
    )
    monthly = _bucket_counts(
        db.query(OutreachStatusDB).filter(OutreachStatusDB.sent_at >= now - timedelta(days=90)).all(),
        "sent_at",
        90,
    )

    return APIResponse(
        success=True,
        data=AnalyticsSeries(
            daily_outreach=build_timeseries(7, daily),
            weekly_outreach=build_timeseries(28, weekly),
            monthly_outreach=build_timeseries(90, monthly),
            professors_discovered=db.query(ProfessorDB).count(),
            drafts_generated=db.query(EmailDraftDB).count(),
            emails_sent=db.query(EmailDraftDB).filter(EmailDraftDB.status == DraftStatus.SENT).count(),
            responses_received=db.query(OutreachStatusDB).filter(OutreachStatusDB.response_received.is_(True)).count(),
        ),
    )


def _bucket_counts(rows: list[object], attribute: str, _: int) -> dict:
    buckets: dict = {}
    for row in rows:
        value = getattr(row, attribute)
        if not value:
            continue
        bucket_date = value.date()
        buckets[bucket_date] = buckets.get(bucket_date, 0) + 1
    return buckets


def _response_rate(db: Session) -> int:
    sent = db.query(OutreachStatusDB).filter(OutreachStatusDB.sent_at.is_not(None)).count()
    if sent == 0:
        return 0
    responses = db.query(OutreachStatusDB).filter(OutreachStatusDB.response_received.is_(True)).count()
    return int((responses / sent) * 100)
