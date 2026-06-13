from datetime import datetime
from pydantic import Field
from typing import Any, Optional
from app.models.base import TimestampedModel


class Document(TimestampedModel):
    user_id: str = Field(..., description="Owning user identifier")
    filename: str = Field(..., description="Original or current filename")
    size: int = Field(..., ge=0)
    mime_type: str = Field(..., description="Stored MIME type")
    uploaded_at: datetime | None = Field(default=None, description="Upload timestamp")
    preview_text: Optional[str] = Field(default=None, description="Extracted preview text")
    metadata: dict[str, Any] = Field(default_factory=dict)
