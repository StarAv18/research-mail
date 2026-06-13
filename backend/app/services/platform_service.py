import uuid
from datetime import date, datetime, timedelta
from typing import Any
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.models.db_models import (
    ActivityLogDB,
    SearchHistoryDB,
    UserDB,
)


def get_or_create_default_user(db: Session) -> UserDB:
    settings = get_settings()
    user = db.query(UserDB).filter(UserDB.email == settings.DEFAULT_USER_EMAIL).first()
    if user:
        return user

    user = UserDB(
        email=settings.DEFAULT_USER_EMAIL,
        full_name=settings.DEFAULT_USER_NAME,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def log_activity(
    db: Session,
    user_id: uuid.UUID,
    event_type: str,
    entity_type: str,
    entity_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> ActivityLogDB:
    log = ActivityLogDB(
        user_id=user_id,
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details or {},
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def record_search(
    db: Session,
    user_id: uuid.UUID,
    query: str,
    research_area: str,
    institution: str,
    country: str,
    region: str,
    results_count: int,
) -> SearchHistoryDB:
    search = SearchHistoryDB(
        user_id=user_id,
        query=query,
        research_area=research_area,
        institution=institution,
        country=country,
        region=region,
        results_count=results_count,
    )
    db.add(search)
    db.commit()
    db.refresh(search)
    return search


def build_timeseries(days: int, buckets: dict[date, int]) -> list[dict[str, int | str]]:
    today = datetime.utcnow().date()
    series = []
    for offset in range(days - 1, -1, -1):
        bucket_date = today - timedelta(days=offset)
        series.append({
            "date": bucket_date.isoformat(),
            "value": buckets.get(bucket_date, 0),
        })
    return series
