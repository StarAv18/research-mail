from typing import List
from app.models.outreach import OutreachHistory
from app.repository.base import BaseRepository
from app.repository.json_base import BaseJSONRepository
from abc import abstractmethod

class OutreachRepository(BaseRepository[OutreachHistory]):
    """
    Abstract interface for OutreachHistory persistence.
    """
    @abstractmethod
    async def get_by_email(self, email: str) -> List[OutreachHistory]:
        """Find all history records for a specific email."""
        pass

    @abstractmethod
    async def count_sent_today(self) -> int:
        """Count how many emails were sent today."""
        pass

class JSONOutreachRepository(BaseJSONRepository[OutreachHistory], OutreachRepository):
    """
    File-based JSON implementation of OutreachRepository.
    """

    def __init__(self):
        super().__init__(filename="outreach_history.json", model_class=OutreachHistory)

    async def get_by_email(self, email: str) -> List[OutreachHistory]:
        """Find all history records for a specific email."""
        records = await self.list_all()
        return [r for r in records if r.professor_email.lower() == email.lower()]

    async def count_sent_today(self) -> int:
        """Count how many emails were sent today."""
        from datetime import datetime
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        records = await self.list_all()
        return len([r for r in records if r.sent_at >= today_start])
