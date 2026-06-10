from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, EmailStr
from typing import List
from uuid import UUID
import asyncio
import smtplib
from email.mime.text import MIMEText
from app.models.draft import Draft, DraftStatus
from app.models.response import APIResponse
from app.api.deps import get_draft_repo
from app.repository.draft_repository import DraftRepository

router = APIRouter()

class DraftProfessor(BaseModel):
    name: str
    university: str
    email: EmailStr | None = None
    website: str | None = None
    research_interests: list[str] = []
    recent_work: str = ""
    biography: str = ""

class GenerateDraftsRequest(BaseModel):
    professors: list[DraftProfessor]
    sender_name: str = "A prospective research intern"
    sender_university: str = "my university"
    sender_background: str = "I am interested in research opportunities and would value the chance to contribute to your lab."

class SendDraftResponse(BaseModel):
    message_id: str

@router.post("/", response_model=APIResponse[Draft])
async def create_draft(
    draft: Draft,
    repo: DraftRepository = Depends(get_draft_repo)
) -> APIResponse[Draft]:
    """Create a new email draft."""
    new_draft = await repo.create(draft)
    return APIResponse(success=True, data=new_draft, message="Draft created successfully")

@router.get("/", response_model=APIResponse[List[Draft]])
async def list_drafts(
    query: str | None = None,
    repo: DraftRepository = Depends(get_draft_repo)
) -> APIResponse[List[Draft]]:
    """List all drafts, optionally filtered by search query."""
    if query:
        drafts = await repo.search(query)
    else:
        drafts = await repo.list_all()
    return APIResponse(success=True, data=drafts)

@router.post("/generate", response_model=APIResponse[List[Draft]])
async def generate_drafts(
    request: GenerateDraftsRequest,
    repo: DraftRepository = Depends(get_draft_repo)
) -> APIResponse[List[Draft]]:
    """Generate local outreach drafts from discovered professor rows."""
    created: list[Draft] = []
    for professor in request.professors:
        if not professor.email:
            continue
        interests = ", ".join(professor.research_interests[:3]) or "your research"
        recent_work = professor.recent_work or professor.biography[:220] or "your recent work"
        subject = f"Research internship inquiry - {interests[:80]}"
        body = (
            f"Dear Professor {professor.name.split()[-1]},\n\n"
            f"My name is {request.sender_name}, and I am a student at {request.sender_university}. "
            f"I am writing to ask about possible research internship or assistantship opportunities in your group.\n\n"
            f"I was especially interested in your work on {interests}. {recent_work}\n\n"
            f"{request.sender_background}\n\n"
            "If you are open to it, I would be grateful for the opportunity to share more about my background "
            "or discuss whether there may be a fit with your current projects.\n\n"
            "Thank you for your time and consideration.\n\n"
            f"Sincerely,\n{request.sender_name}"
        )
        draft = Draft(
            professor_name=professor.name,
            professor_email=professor.email,
            university=professor.university,
            subject=subject,
            body=body,
            status=DraftStatus.PENDING,
        )
        created.append(await repo.create(draft))

    return APIResponse(success=True, data=created, message=f"Created {len(created)} drafts")

@router.get("/{draft_id}", response_model=APIResponse[Draft])
async def get_draft(
    draft_id: UUID,
    repo: DraftRepository = Depends(get_draft_repo)
) -> APIResponse[Draft]:
    """Get a specific draft by ID."""
    draft = await repo.get_by_id(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return APIResponse(success=True, data=draft)

@router.put("/{draft_id}", response_model=APIResponse[Draft])
async def update_draft(
    draft_id: UUID,
    draft: Draft,
    repo: DraftRepository = Depends(get_draft_repo)
) -> APIResponse[Draft]:
    """Update an existing draft."""
    try:
        updated = await repo.update(draft_id, draft)
        return APIResponse(success=True, data=updated, message="Draft updated successfully")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{draft_id}", response_model=APIResponse[bool])
async def delete_draft(
    draft_id: UUID,
    repo: DraftRepository = Depends(get_draft_repo)
) -> APIResponse[bool]:
    """Delete a draft."""
    success = await repo.delete(draft_id)
    if not success:
        raise HTTPException(status_code=404, detail="Draft not found")
    return APIResponse(success=True, data=True, message="Draft deleted successfully")

@router.post("/{draft_id}/send-gmail", response_model=APIResponse[SendDraftResponse])
async def send_gmail_with_app_password(
    draft_id: UUID,
    x_gmail_address: str | None = Header(default=None),
    x_gmail_app_password: str | None = Header(default=None),
    repo: DraftRepository = Depends(get_draft_repo)
) -> APIResponse[SendDraftResponse]:
    """Send a local draft through Gmail SMTP using a user-provided app password."""
    if not x_gmail_address or not x_gmail_app_password:
        raise HTTPException(status_code=400, detail="Gmail address and app password are required")

    draft = await repo.get_by_id(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    message = MIMEText(draft.body)
    message["From"] = x_gmail_address
    message["To"] = draft.professor_email
    message["Subject"] = draft.subject

    def _send() -> str:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as smtp:
            smtp.login(x_gmail_address, x_gmail_app_password)
            result = smtp.send_message(message)
            return str(result) if result else "sent"

    message_id = await asyncio.get_event_loop().run_in_executor(None, _send)
    draft.status = DraftStatus.SENT
    await repo.update(draft_id, draft)
    return APIResponse(success=True, data=SendDraftResponse(message_id=message_id), message="Email sent")
