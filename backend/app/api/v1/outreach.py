from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from uuid import UUID
from app.models.response import APIResponse
from app.models.professor import Professor
from app.models.student_profile import StudentProfile
from app.models.research_summary import ResearchSummary
from app.models.generated_email import GeneratedEmail
from app.api.deps import (
    get_email_gen_service, 
    get_summarization_service, 
    get_safety_service,
    get_bulk_email_service
)
from app.services.email_generation import EmailGenerationService
from app.services.summarization import SummarizationService
from app.services.safety_service import SafetyService
from app.services.bulk_email_service import BulkEmailService

router = APIRouter()

class GenerationRequest(BaseModel):
    professor: Professor
    student: StudentProfile
    research_summary: ResearchSummary
    email_style: str = "Standard Professional"

@router.post("/generate", response_model=APIResponse[GeneratedEmail])
async def generate_outreach_email(
    request: GenerationRequest,
    gen_service: EmailGenerationService = Depends(get_email_gen_service),
    safety_service: SafetyService = Depends(get_safety_service)
) -> APIResponse[GeneratedEmail]:
    """Generate a personalized outreach email after safety checks."""
    
    # Safety Check
    is_safe, reason = await safety_service.is_safe_to_send(request.professor.email)
    if not is_safe:
        raise HTTPException(status_code=400, detail=reason)
        
    email = await gen_service.generate_email(
        professor=request.professor,
        research_summary=request.research_summary,
        student=request.student,
        email_style=request.email_style
    )
    
    return APIResponse(success=True, data=email)

@router.post("/bulk-send", response_model=APIResponse[Dict[str, Any]])
async def bulk_send_emails(
    local_draft_ids: List[UUID], # IDs of local drafts to send
    bulk_service: BulkEmailService = Depends(get_bulk_email_service)
) -> APIResponse[Dict[str, Any]]:
    """Trigger bulk send for multiple drafts."""
    # In a real workflow, we'd ensure provider drafts exist first
    results = await bulk_service.bulk_send(
        provider_draft_ids=["mock_" + str(i) for i in local_draft_ids],
        local_draft_ids=local_draft_ids
    )
    return APIResponse(success=True, data=results)
