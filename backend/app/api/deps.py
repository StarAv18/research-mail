from fastapi import Depends
from app.core.config import get_settings
from app.repository.draft_repository import DraftRepository, JSONDraftRepository
from app.repository.outreach_repository import OutreachRepository, JSONOutreachRepository
from app.services.ai import BaseAIProvider, get_ai_provider
from app.services.email_generation import EmailGenerationService
from app.services.summarization import SummarizationService
from app.services.outreach_service import OutreachService
from app.services.bulk_email_service import BulkEmailService
from app.services.safety_service import SafetyService
from functools import lru_cache

# Repository singletons (since they handle file locking)
@lru_cache
def get_draft_repo() -> DraftRepository:
    return JSONDraftRepository()

@lru_cache
def get_outreach_repo() -> OutreachRepository:
    return JSONOutreachRepository()

# Service Factories
def get_email_gen_service(
    ai_provider: BaseAIProvider = Depends(get_ai_provider)
) -> EmailGenerationService:
    return EmailGenerationService(ai_provider=ai_provider)

def get_summarization_service(
    ai_provider: BaseAIProvider = Depends(get_ai_provider)
) -> SummarizationService:
    return SummarizationService(ai_provider=ai_provider)

def get_outreach_service(
    repo: OutreachRepository = Depends(get_outreach_repo)
) -> OutreachService:
    return OutreachService(repository=repo)

def get_safety_service(
    repo: OutreachRepository = Depends(get_outreach_repo)
) -> SafetyService:
    return SafetyService(outreach_repo=repo)

def get_scraper_service() -> UniversityProfileScraper:
    return UniversityProfileScraper()

def get_bulk_email_service(
    draft_repo: DraftRepository = Depends(get_draft_repo),
    outreach_service: OutreachService = Depends(get_outreach_service)
) -> BulkEmailService:
    # GmailProvider injection would go here in a real scenario
    # For now we use the interface logic
    from app.services.gmail_service import GmailProvider
    return BulkEmailService(
        draft_repository=draft_repo,
        email_provider=GmailProvider(),
        outreach_service=outreach_service
    )
