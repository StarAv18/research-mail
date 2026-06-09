from pydantic import Field, EmailStr
from typing import Optional
from datetime import datetime
from app.models.base import TimestampedModel

class OutreachHistory(TimestampedModel):
    """
    Record of a sent email to a professor.
    
    Attributes:
        professor_email: Recipient's email.
        sent_at: Timestamp when the email was sent.
        status: Delivery status.
        provider: Email provider used (e.g., 'gmail').
        message_id: Unique identifier from the provider.
        subject: Subject of the sent email.
    """
    professor_email: EmailStr = Field(..., description="Email address of the contacted professor")
    sent_at: datetime = Field(default_factory=datetime.now, description="Timestamp of the outreach")
    status: str = Field(default="sent", description="Delivery status of the email")
    provider: str = Field(..., description="Email provider used (e.g., 'gmail')")
    message_id: str = Field(..., description="Unique ID assigned by the email provider")
    subject: str = Field(..., description="Subject of the sent email")
