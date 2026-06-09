from typing import List, Dict, Any
from uuid import UUID
from app.models.draft import Draft, DraftStatus
from app.repository.draft_repository import DraftRepository
from app.services.email_provider import EmailProvider
from app.services.outreach_service import OutreachService
from app.core.logging import get_logger

logger = get_logger(__name__)

class BulkEmailService:
    """
    Orchestrates bulk email operations, including draft creation and sending.
    """

    def __init__(
        self, 
        draft_repository: DraftRepository,
        email_provider: EmailProvider,
        outreach_service: OutreachService
    ):
        self.draft_repo = draft_repository
        self.email_provider = email_provider
        self.outreach_service = outreach_service

    async def create_provider_drafts(self, draft_ids: List[UUID]) -> Dict[str, Any]:
        """
        Create drafts in the email provider's system (e.g., Gmail).
        """
        results = {"success": [], "failed": []}
        for draft_id in draft_ids:
            success, info = await self._process_single_draft_creation(draft_id)
            if success:
                results["success"].append(info)
            else:
                results["failed"].append(info)
        return results

    async def _process_single_draft_creation(self, draft_id: UUID) -> tuple[bool, Dict[str, Any]]:
        """Process creation for a single draft."""
        try:
            draft = await self.draft_repo.get_by_id(draft_id)
            if not draft:
                return False, {"id": str(draft_id), "error": "Draft not found"}
            
            provider_id = await self.email_provider.create_draft(draft)
            draft.status = DraftStatus.READY
            await self.draft_repo.update(draft_id, draft)
            
            return True, {"id": str(draft_id), "provider_id": provider_id}
        except Exception as e:
            logger.error(f"Failed to create provider draft for {draft_id}: {e}")
            return False, {"id": str(draft_id), "error": str(e)}

    async def bulk_send(self, provider_draft_ids: List[str], local_draft_ids: List[UUID]) -> Dict[str, Any]:
        """
        Send multiple drafts and track their success.
        """
        results = {"sent": [], "failed": []}
        for p_id, l_id in zip(provider_draft_ids, local_draft_ids):
            success, info = await self._process_single_send(p_id, l_id)
            if success:
                results["sent"].append(info)
            else:
                results["failed"].append(info)
        return results

    async def _process_single_send(self, provider_id: str, local_id: UUID) -> tuple[bool, Dict[str, Any]]:
        """Process sending for a single draft."""
        try:
            draft = await self.draft_repo.get_by_id(local_id)
            if not draft:
                return False, {"id": str(local_id), "error": "Local draft not found"}

            message_id = await self.email_provider.send_draft(provider_id)
            
            # Track in outreach history
            await self.outreach_service.track_outreach(
                email=draft.professor_email,
                subject=draft.subject,
                message_id=message_id
            )
            
            # Update local draft status
            draft.status = DraftStatus.SENT
            await self.draft_repo.update(local_id, draft)
            
            return True, {"id": str(local_id), "message_id": message_id}
        except Exception as e:
            logger.error(f"Bulk send failed for {local_id}: {e}")
            return False, {"id": str(local_id), "error": str(e)}
