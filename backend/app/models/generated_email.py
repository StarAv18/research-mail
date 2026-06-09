from pydantic import Field
from typing import Optional
from app.models.base import TimestampedModel
from app.models.enums import AIProvider

class GeneratedEmail(TimestampedModel):
    """
    Represents a personalized email generated for a professor.
    
    Attributes:
        subject: The email subject line.
        body: The full content of the email.
        recipient_name: Name of the professor.
        provider_used: The AI provider used to generate the email.
        personalization_notes: Brief notes on what was personalized.
    """
    subject: str = Field(..., description="The email subject line", min_length=5, max_length=200)
    body: str = Field(..., description="The full content of the email", min_length=100, max_length=20000)
    recipient_name: str = Field(..., description="Name of the professor")
    provider_used: AIProvider = Field(..., description="The AI provider used to generate the email")
    personalization_notes: Optional[str] = Field(None, description="Brief notes on what was personalized", max_length=1000)
