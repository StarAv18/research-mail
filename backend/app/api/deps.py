from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.db import get_db
from app.repository.draft_repository import DraftRepository
from app.repository.postgres_draft_repository import PostgresDraftRepository
from app.repository.outreach_repository import OutreachRepository, JSONOutreachRepository
from app.services.ai import BaseAIProvider, get_ai_provider
from app.services.email_generation import EmailGenerationService
from app.services.summarization import SummarizationService
from app.services.outreach_service import OutreachService
from app.services.bulk_email_service import BulkEmailService
from app.services.safety_service import SafetyService
from app.services.university_scraper import UniversityProfileScraper
from functools import lru_cache

# Repository singletons (since they handle file locking)
def get_draft_repo(db: Session = Depends(get_db)) -> DraftRepository:
    return PostgresDraftRepository(db)

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
    db: Session = Depends(get_db),
    draft_repo: DraftRepository = Depends(get_draft_repo),
    outreach_service: OutreachService = Depends(get_outreach_service)
) -> BulkEmailService:
    """
    Dependency injection factory for BulkEmailService.
    In a production app, the user_email would come from the auth context.
    """
    from app.services.gmail_service import GmailProvider
    from app.models.db_models import UserCredentialsDB
    
    # Try to get the first available credential as a fallback for demo/dev
    creds = db.query(UserCredentialsDB).first()
    user_email = creds.email if creds else "demo@example.com"
    
    return BulkEmailService(
        draft_repository=draft_repo,
        email_provider=GmailProvider(db=db, user_email=user_email),
        outreach_service=outreach_service
    )
