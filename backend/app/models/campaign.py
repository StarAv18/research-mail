from datetime import datetime
from pydantic import Field
from typing import Optional
from app.models.base import TimestampedModel


class Campaign(TimestampedModel):
    user_id: str = Field(..., description="Owning user identifier")
    name: str = Field(..., min_length=3, max_length=255)
    status: str = Field(default="draft")
    total_drafts: int = Field(default=0, ge=0)
    sent_count: int = Field(default=0, ge=0)
    failed_count: int = Field(default=0, ge=0)
    retry_count: int = Field(default=0, ge=0)
    last_error: Optional[str] = None
    executed_at: Optional[datetime] = None


class CampaignExecutionResult(TimestampedModel):
    campaign_id: str
    sent: int = 0
    failed: int = 0
    retried: int = 0
