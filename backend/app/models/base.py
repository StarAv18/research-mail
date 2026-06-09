from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
import uuid

class BaseProjectModel(BaseModel):
    """
    Base model for all project-related data.
    Provides standard Pydantic v2 configuration and common fields.
    """
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        populate_by_name=True,
        str_strip_whitespace=True
    )

class TimestampedModel(BaseProjectModel):
    """
    Base model that includes ID and timestamp fields for persistence.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique identifier")
    created_at: datetime = Field(default_factory=datetime.now, description="Record creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Record last update timestamp")
