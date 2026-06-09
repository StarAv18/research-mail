from pydantic import Field, EmailStr
from typing import Optional
from enum import Enum
from app.models.base import TimestampedModel

class DraftStatus(str, Enum):
    """Status of an email draft."""
    PENDING = "pending"
    EDITED = "edited"
    READY = "ready"
    SENT = "sent"
    FAILED = "failed"
    ARCHIVED = "archived"

class Draft(TimestampedModel):
    """
    Represents an email draft for outreach.
    
    Attributes:
        professor_name: Name of the recipient professor.
        professor_email: Email address of the recipient.
        university: Affiliated university.
        subject: Email subject line.
        body: Email body content.
        status: Current status of the draft.
    """
    professor_name: str = Field(..., description="Name of the recipient professor")
    professor_email: EmailStr = Field(..., description="Email address of the recipient")
    university: str = Field(..., description="Affiliated university")
    subject: str = Field(..., description="Email subject line", min_length=5, max_length=200)
    body: str = Field(..., description="Email body content", min_length=100)
    status: DraftStatus = Field(default=DraftStatus.PENDING, description="Current status of the draft")
