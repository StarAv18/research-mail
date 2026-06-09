from typing import List, Optional
from uuid import UUID
from app.models.draft import Draft
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
