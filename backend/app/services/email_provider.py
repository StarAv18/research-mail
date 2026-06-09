from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.draft import Draft

class EmailProvider(ABC):
    """
    Abstract interface for email service providers (Gmail, Outlook, etc.).
    """

    @abstractmethod
    async def create_draft(self, draft: Draft) -> str:
        """
        Create a draft in the provider's system.
        
        Returns:
            The provider's unique ID for the draft.
        """
        pass

    @abstractmethod
    async def send_draft(self, draft_id: str) -> str:
        """
        Send an existing draft.
        
        Returns:
            The provider's unique message ID.
        """
        pass

    @abstractmethod
    async def list_drafts(self) -> List[dict]:
        """List drafts from the provider."""
        pass
