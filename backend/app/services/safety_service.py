from datetime import datetime
from typing import List
from app.repository.outreach_repository import OutreachRepository
from app.core.logging import get_logger

logger = get_logger(__name__)

class SafetyService:
    """
    Implements safety checks and guardrails for email outreach.
    """

    def __init__(self, outreach_repo: OutreachRepository, daily_limit: int = 50):
        self.outreach_repo = outreach_repo
        self.daily_limit = daily_limit

    async def is_safe_to_send(self, email: str) -> tuple[bool, str]:
        """
        Verify if it's safe to send an email to a recipient.
        """
        # 1. Check for duplicates
        history = await self.outreach_repo.get_by_email(email)
        if history:
            # Sort by sent_at descending to get the most recent contact
            latest = sorted(history, key=lambda x: x.sent_at, reverse=True)[0]
            return False, f"Already contacted this professor on {latest.sent_at.strftime('%Y-%m-%d')}"

        # 2. Check daily limits
        today_sent_count = await self.outreach_repo.count_sent_today()
        if today_sent_count >= self.daily_limit:
            return False, f"Daily send limit of {self.daily_limit} reached"

        return True, "Safe to send"

    async def get_remaining_quota(self) -> int:
        """
        Calculate how many emails can still be sent today.
        """
        today_sent_count = await self.outreach_repo.count_sent_today()
        return max(0, self.daily_limit - today_sent_count)
