import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.activity import ActivityLog
from app.models.db_models import ActivityLogDB
from app.models.response import APIResponse
from app.services.platform_service import get_or_create_default_user

router = APIRouter()


@router.get("/", response_model=APIResponse[list[ActivityLog]])
async def list_activity(
    limit: int = Query(50, ge=1, le=200),
    event_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> APIResponse[list[ActivityLog]]:
    user = get_or_create_default_user(db)
    query = db.query(ActivityLogDB).filter(ActivityLogDB.user_id == user.id)
    if event_type:
        query = query.filter(ActivityLogDB.event_type == event_type)
    rows = query.order_by(ActivityLogDB.created_at.desc()).limit(limit).all()
    return APIResponse(success=True, data=[_to_activity(row) for row in rows])


def _to_activity(activity: ActivityLogDB) -> ActivityLog:
    return ActivityLog(
        id=activity.id,
        user_id=str(activity.user_id),
        event_type=activity.event_type,
        entity_type=activity.entity_type,
        entity_id=activity.entity_id,
        details=activity.details or {},
        created_at=activity.created_at,
        updated_at=activity.updated_at,
    )
