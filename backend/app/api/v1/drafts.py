import asyncio
from email.mime.text import MIMEText
import smtplib
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.api.deps import get_draft_repo
from app.core.db import get_db
from app.models.draft import Draft, DraftStatus, DraftVersion
from app.models.db_models import DocumentDB, EmailDraftDB, OutreachStatusDB, ProfessorDB
from app.models.response import APIResponse
from app.repository.draft_repository import DraftRepository
from app.services.platform_service import get_or_create_default_user, log_activity

router = APIRouter()


class DraftProfessor(BaseModel):
    name: str
    university: str
    country: str | None = None
    email: EmailStr | None = None
    website: str | None = None
    research_interests: list[str] = []
    recent_publications: list[str] = []
    recent_work: str = ""
    biography: str = ""


class GenerateDraftsRequest(BaseModel):
    professors: list[DraftProfessor]
    sender_name: str = "A prospective research intern"
    sender_university: str = "my university"
    sender_background: str = "I am interested in research opportunities and would value the chance to contribute to your lab."


class SaveVersionRequest(BaseModel):
    subject: str
    body: str
    editor: str = "user"
    change_reason: str = "manual edit"


class RegenerateDraftRequest(BaseModel):
    sender_name: str = "A prospective research intern"
    sender_university: str = "my university"
    sender_background: str = "I am interested in research opportunities and would value the chance to contribute to your lab."


class SendDraftResponse(BaseModel):
    message_id: str


@router.post("/", response_model=APIResponse[Draft])
async def create_draft(
    draft: Draft,
    repo: DraftRepository = Depends(get_draft_repo),
) -> APIResponse[Draft]:
    new_draft = await repo.create(draft)
    return APIResponse(success=True, data=new_draft, message="Draft created successfully")


@router.get("/", response_model=APIResponse[List[Draft]])
async def list_drafts(
    query: str | None = None,
    repo: DraftRepository = Depends(get_draft_repo),
) -> APIResponse[List[Draft]]:
    drafts = await repo.search(query) if query else await repo.list_all()
    return APIResponse(success=True, data=drafts)


@router.post("/generate", response_model=APIResponse[List[Draft]])
async def generate_drafts(
    request: GenerateDraftsRequest,
    db: Session = Depends(get_db),
    repo: DraftRepository = Depends(get_draft_repo),
) -> APIResponse[List[Draft]]:
    created: list[Draft] = []
    user = get_or_create_default_user(db)
    documents = (
        db.query(DocumentDB)
        .filter(DocumentDB.user_id == user.id)
        .order_by(DocumentDB.uploaded_at.desc())
        .limit(3)
        .all()
    )
    document_context = _build_document_context(documents)

    for professor in request.professors:
        if not professor.email:
            continue

        subject = _build_subject(professor)
        body, notes = _build_personalized_email(professor, request, document_context)
        draft = Draft(
            professor_name=professor.name,
            professor_email=professor.email,
            university=professor.university,
            subject=subject,
            body=body,
            status=DraftStatus.PENDING,
            personalization_notes=notes,
            current_version=1,
            version_count=1,
        )
        created_draft = await repo.create(draft)
        created.append(created_draft)
        log_activity(
            db,
            user.id,
            event_type="draft_create",
            entity_type="draft",
            entity_id=str(created_draft.id),
            details={"professor": created_draft.professor_name},
        )

    return APIResponse(success=True, data=created, message=f"Created {len(created)} drafts")


@router.get("/{draft_id}", response_model=APIResponse[Draft])
async def get_draft(
    draft_id: UUID,
    repo: DraftRepository = Depends(get_draft_repo),
) -> APIResponse[Draft]:
    draft = await repo.get_by_id(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return APIResponse(success=True, data=draft)


@router.put("/{draft_id}", response_model=APIResponse[Draft])
async def update_draft(
    draft_id: UUID,
    draft: Draft,
    db: Session = Depends(get_db),
    repo: DraftRepository = Depends(get_draft_repo),
) -> APIResponse[Draft]:
    try:
        updated = await repo.save_version(
            draft_id,
            subject=draft.subject,
            body=draft.body,
            editor="user",
            change_reason="manual edit",
        )
        updated.status = DraftStatus.EDITED
        updated.personalization_notes = draft.personalization_notes or updated.personalization_notes
        updated = await repo.update(draft_id, updated)
        user = get_or_create_default_user(db)
        log_activity(
            db,
            user.id,
            event_type="draft_edit",
            entity_type="draft",
            entity_id=str(draft_id),
            details={"subject": draft.subject},
        )
        return APIResponse(success=True, data=updated, message="Draft updated successfully")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{draft_id}/versions", response_model=APIResponse[List[DraftVersion]])
async def list_draft_versions(
    draft_id: UUID,
    repo: DraftRepository = Depends(get_draft_repo),
) -> APIResponse[List[DraftVersion]]:
    return APIResponse(success=True, data=await repo.list_versions(draft_id))


@router.post("/{draft_id}/versions", response_model=APIResponse[Draft])
async def save_draft_version(
    draft_id: UUID,
    request: SaveVersionRequest,
    db: Session = Depends(get_db),
    repo: DraftRepository = Depends(get_draft_repo),
) -> APIResponse[Draft]:
    try:
        draft = await repo.save_version(
            draft_id,
            subject=request.subject,
            body=request.body,
            editor=request.editor,
            change_reason=request.change_reason,
        )
        user = get_or_create_default_user(db)
        log_activity(
            db,
            user.id,
            event_type="draft_version",
            entity_type="draft",
            entity_id=str(draft_id),
            details={"version": draft.current_version, "reason": request.change_reason},
        )
        return APIResponse(success=True, data=draft, message="Draft version saved")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/{draft_id}/regenerate", response_model=APIResponse[Draft])
async def regenerate_draft(
    draft_id: UUID,
    request: RegenerateDraftRequest,
    db: Session = Depends(get_db),
    repo: DraftRepository = Depends(get_draft_repo),
) -> APIResponse[Draft]:
    draft = await repo.get_by_id(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    professor_row = db.query(ProfessorDB).filter(ProfessorDB.email == draft.professor_email).first()
    professor = DraftProfessor(
        name=draft.professor_name,
        university=draft.university,
        country=professor_row.country if professor_row else None,
        email=draft.professor_email,
        website=professor_row.website if professor_row else None,
        research_interests=list(professor_row.research_interests or []) if professor_row else [],
        recent_publications=list(professor_row.recent_publications or []) if professor_row else [],
        recent_work=(professor_row.biography or "")[:240] if professor_row else "",
        biography=professor_row.biography if professor_row else "",
    )
    user = get_or_create_default_user(db)
    documents = (
        db.query(DocumentDB)
        .filter(DocumentDB.user_id == user.id)
        .order_by(DocumentDB.uploaded_at.desc())
        .limit(3)
        .all()
    )
    body, notes = _build_personalized_email(professor, request, _build_document_context(documents))
    regenerated = await repo.save_version(
        draft_id,
        subject=_build_subject(professor),
        body=body,
        editor="system",
        change_reason="regenerated",
    )
    regenerated.personalization_notes = notes
    regenerated.status = DraftStatus.EDITED
    regenerated = await repo.update(draft_id, regenerated)
    log_activity(
        db,
        user.id,
        event_type="draft_regenerate",
        entity_type="draft",
        entity_id=str(draft_id),
        details={"version": regenerated.current_version},
    )
    return APIResponse(success=True, data=regenerated, message="Draft regenerated")


@router.delete("/{draft_id}", response_model=APIResponse[bool])
async def delete_draft(
    draft_id: UUID,
    repo: DraftRepository = Depends(get_draft_repo),
) -> APIResponse[bool]:
    success = await repo.delete(draft_id)
    if not success:
        raise HTTPException(status_code=404, detail="Draft not found")
    return APIResponse(success=True, data=True, message="Draft deleted successfully")


@router.post("/{draft_id}/send-gmail", response_model=APIResponse[SendDraftResponse])
async def send_gmail_with_app_password(
    draft_id: UUID,
    x_gmail_address: str | None = Header(default=None),
    x_gmail_app_password: str | None = Header(default=None),
    db: Session = Depends(get_db),
    repo: DraftRepository = Depends(get_draft_repo),
) -> APIResponse[SendDraftResponse]:
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
    updated = await repo.update(draft_id, draft)
    draft_row = db.query(EmailDraftDB).filter(EmailDraftDB.id == draft_id).first()
    professor_row = db.query(ProfessorDB).filter(ProfessorDB.email == updated.professor_email).first()
    db.add(
        OutreachStatusDB(
            professor_id=professor_row.id if professor_row else None,
            draft_id=draft_row.id if draft_row else None,
            campaign_id=draft_row.campaign_id if draft_row else None,
            recipient_email=updated.professor_email,
            status="sent",
            provider="gmail",
            message_id=message_id,
            sent_at=__import__("datetime").datetime.utcnow(),
        )
    )
    db.commit()
    user = get_or_create_default_user(db)
    log_activity(
        db,
        user.id,
        event_type="email_send",
        entity_type="draft",
        entity_id=str(draft_id),
        details={"recipient": updated.professor_email},
    )
    return APIResponse(success=True, data=SendDraftResponse(message_id=message_id), message="Email sent")


def _build_subject(professor: DraftProfessor) -> str:
    top_interest = professor.research_interests[0] if professor.research_interests else "your recent work"
    return f"Possible research fit with your {top_interest.lower()} work"


def _build_document_context(documents: list[DocumentDB]) -> str:
    snippets = [(document.extracted_text or "")[:400] for document in documents if document.extracted_text]
    return "\n".join(snippets[:2]).strip()


def _build_personalized_email(professor: DraftProfessor, request: GenerateDraftsRequest | RegenerateDraftRequest, document_context: str) -> tuple[str, str]:
    interests = ", ".join(professor.research_interests[:3]) or "your recent work"
    publication_line = "; ".join(professor.recent_publications[:2]) or professor.recent_work or "your recent publications"
    institution_line = professor.university if not professor.country else f"{professor.university} in {professor.country}"
    document_line = ""
    if document_context:
        document_line = (
            "A short sample of my prior work that aligns with this direction includes: "
            f"{document_context[:260].replace(chr(10), ' ')}.\n\n"
        )
    last_name = professor.name.split()[-1]
    body = (
        f"Dear Professor {last_name},\n\n"
        f"My name is {request.sender_name}, and I am currently at {request.sender_university}. "
        f"I am reaching out because your research group at {institution_line} is working on questions that closely overlap with my interests.\n\n"
        f"In particular, I was drawn to your work on {interests}. "
        f"The way your recent output connects to {publication_line} stood out to me as a direction where I could contribute meaningfully.\n\n"
        f"{request.sender_background}\n\n"
        f"{document_line}"
        "If there is an opportunity to support an ongoing project, I would be glad to share a concise summary of my background and discuss where I might be useful.\n\n"
        f"Best regards,\n{request.sender_name}"
    )
    notes = f"Personalized using interests ({interests}), publications ({publication_line}), institution ({institution_line})"
    if document_context:
        notes += ", and uploaded documents"
    return body, notes
