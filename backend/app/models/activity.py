from pydantic import Field
from typing import Any
from app.models.base import TimestampedModel


class ActivityLog(TimestampedModel):
    user_id: str = Field(..., description="Owning user identifier")
    event_type: str = Field(..., description="Action category")
    entity_type: str = Field(..., description="Affected entity")
    entity_id: str | None = Field(default=None)
    details: dict[str, Any] = Field(default_factory=dict)
