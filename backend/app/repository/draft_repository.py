from typing import List, Optional
from uuid import UUID
from app.models.draft import Draft, DraftVersion
from app.repository.base import BaseRepository
from app.repository.json_base import BaseJSONRepository
from abc import abstractmethod

class DraftRepository(BaseRepository[Draft]):
    """
    Abstract interface for Draft persistence.
    """
    @abstractmethod
    async def search(self, query: str) -> List[Draft]:
        """Search drafts by name, email, or university."""
        pass

    @abstractmethod
    async def list_versions(self, id: UUID) -> List[DraftVersion]:
        """List saved versions for a draft."""
        pass

    @abstractmethod
    async def save_version(
        self,
        id: UUID,
        subject: str,
        body: str,
        editor: str = "system",
        change_reason: str = "manual update",
    ) -> Draft:
        """Create a new version and make it current."""
        pass

class JSONDraftRepository(BaseJSONRepository[Draft], DraftRepository):
    """
    File-based JSON implementation of DraftRepository.
    """

    def __init__(self):
        super().__init__(filename="drafts.json", model_class=Draft)

    async def search(self, query: str) -> List[Draft]:
        """Search drafts by name, email, or university."""
        drafts = await self.list_all()
        query = query.lower()
        return [
            d for d in drafts 
            if query in d.professor_name.lower() or 
               query in d.professor_email.lower() or 
               query in d.university.lower()
        ]

    async def list_versions(self, id: UUID) -> List[DraftVersion]:
        draft = await self.get_by_id(id)
        if not draft:
            return []
        return [
            DraftVersion(
                draft_id=str(draft.id),
                version_number=draft.current_version,
                subject=draft.subject,
                body=draft.body,
            )
        ]

    async def save_version(
        self,
        id: UUID,
        subject: str,
        body: str,
        editor: str = "system",
        change_reason: str = "manual update",
    ) -> Draft:
        draft = await self.get_by_id(id)
        if not draft:
            raise ValueError(f"Draft with ID {id} not found")
        draft.subject = subject
        draft.body = body
        draft.current_version += 1
        draft.version_count = draft.current_version
        draft.personalization_notes = draft.personalization_notes or change_reason
        return await self.update(id, draft)
