from typing import List, Optional
from app.models.outreach import OutreachHistory
from app.repository.outreach_repository import OutreachRepository
from app.core.logging import get_logger

logger = get_logger(__name__)

class OutreachService:
    """
    Business logic for tracking and validating outreach attempts.
    
    This service ensures we don't contact the same professor multiple times
    and maintains a history of all communications.
    """

    def __init__(self, repository: OutreachRepository):
        """
        Initialize the service with a persistence repository.
        """
        self.repository = repository

    async def can_contact(self, email: str) -> bool:
        """
        Check if a professor can be contacted.
        
        Args:
            email: The professor's email address.
            
        Returns:
            True if no previous outreach exists, False otherwise.
        """
        history = await self.repository.get_by_email(email)
        return len(history) == 0

    async def track_outreach(
        self, 
        email: str, 
        subject: str, 
        message_id: str, 
        provider: str = "gmail"
    ) -> OutreachHistory:
        """
        Record a successful outreach attempt.
        
        Args:
            email: Recipient's email.
            subject: Sent email subject.
            message_id: Provider's unique ID.
            provider: The email provider used.
            
        Returns:
            The created OutreachHistory record.
        """
        history = OutreachHistory(
            professor_email=email,
            subject=subject,
            message_id=message_id,
            provider=provider
        )
        return await self.repository.create(history)

    async def get_history(self, email: Optional[str] = None) -> List[OutreachHistory]:
        """
        Retrieve outreach history.
        
        Args:
            email: Optional email to filter history.
            
        Returns:
            A list of history records.
        """
        if email:
            return await self.repository.get_by_email(email)
        return await self.repository.list_all()
