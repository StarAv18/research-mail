import asyncio
from datetime import datetime
from email.mime.text import MIMEText
import smtplib
import uuid
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.campaign import Campaign, CampaignExecutionResult
from app.models.draft import DraftStatus
from app.models.db_models import EmailCampaignDB, EmailDraftDB, OutreachStatusDB, ProfessorDB
from app.models.response import APIResponse
from app.services.platform_service import get_or_create_default_user, log_activity

router = APIRouter()


class CampaignCreateRequest(BaseModel):
    name: str = Field(..., min_length=3)
    draft_ids: list[uuid.UUID] = Field(default_factory=list)


class CampaignDetailResponse(BaseModel):
    campaign: Campaign
    draft_ids: list[str]


@router.post("/", response_model=APIResponse[Campaign])
async def create_campaign(
    request: CampaignCreateRequest,
    db: Session = Depends(get_db),
) -> APIResponse[Campaign]:
    user = get_or_create_default_user(db)
    campaign = EmailCampaignDB(
        user_id=user.id,
        name=request.name,
        total_drafts=len(request.draft_ids),
        status="draft",
    )
    db.add(campaign)
    db.flush()
    if request.draft_ids:
        drafts = db.query(EmailDraftDB).filter(EmailDraftDB.id.in_(request.draft_ids)).all()
        for draft in drafts:
            draft.campaign_id = campaign.id
    db.commit()
    db.refresh(campaign)
    log_activity(
        db,
        user.id,
        event_type="campaign_create",
        entity_type="campaign",
        entity_id=str(campaign.id),
        details={"name": campaign.name, "total_drafts": campaign.total_drafts},
    )
    return APIResponse(success=True, data=_to_campaign(campaign), message="Campaign created")


@router.get("/", response_model=APIResponse[list[Campaign]])
async def list_campaigns(db: Session = Depends(get_db)) -> APIResponse[list[Campaign]]:
    user = get_or_create_default_user(db)
    campaigns = (
        db.query(EmailCampaignDB)
        .filter(EmailCampaignDB.user_id == user.id)
        .order_by(EmailCampaignDB.created_at.desc())
        .all()
    )
    return APIResponse(success=True, data=[_to_campaign(item) for item in campaigns])


@router.get("/{campaign_id}", response_model=APIResponse[CampaignDetailResponse])
async def get_campaign(campaign_id: uuid.UUID, db: Session = Depends(get_db)) -> APIResponse[CampaignDetailResponse]:
    campaign = db.query(EmailCampaignDB).filter(EmailCampaignDB.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    drafts = db.query(EmailDraftDB).filter(EmailDraftDB.campaign_id == campaign.id).all()
    return APIResponse(
        success=True,
        data=CampaignDetailResponse(campaign=_to_campaign(campaign), draft_ids=[str(draft.id) for draft in drafts]),
    )


@router.post("/{campaign_id}/execute", response_model=APIResponse[CampaignExecutionResult])
async def execute_campaign(
    campaign_id: uuid.UUID,
    x_gmail_address: str | None = Header(default=None),
    x_gmail_app_password: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> APIResponse[CampaignExecutionResult]:
    if not x_gmail_address or not x_gmail_app_password:
        raise HTTPException(status_code=400, detail="Gmail address and app password are required")

    campaign = db.query(EmailCampaignDB).filter(EmailCampaignDB.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    drafts = (
        db.query(EmailDraftDB, ProfessorDB)
        .join(ProfessorDB)
        .filter(EmailDraftDB.campaign_id == campaign.id)
        .all()
    )
    if not drafts:
        raise HTTPException(status_code=400, detail="Campaign has no linked drafts")

    sent = 0
    failed = 0
    for draft, professor in drafts:
        try:
            message_id = await _send_message(
                gmail_address=x_gmail_address,
                gmail_app_password=x_gmail_app_password,
                recipient=professor.email,
                subject=draft.subject,
                body=draft.body,
            )
            draft.status = DraftStatus.SENT
            sent += 1
            db.add(
                OutreachStatusDB(
                    professor_id=professor.id,
                    draft_id=draft.id,
                    campaign_id=campaign.id,
                    recipient_email=professor.email,
                    status="sent",
                    provider="gmail",
                    message_id=message_id,
                    sent_at=datetime.utcnow(),
                )
            )
        except Exception as exc:
            failed += 1
            draft.status = DraftStatus.FAILED
            db.add(
                OutreachStatusDB(
                    professor_id=professor.id,
                    draft_id=draft.id,
                    campaign_id=campaign.id,
                    recipient_email=professor.email,
                    status="failed",
                    provider="gmail",
                    error_message=str(exc),
                )
            )

    campaign.status = "completed" if failed == 0 else "completed_with_failures"
    campaign.sent_count = sent
    campaign.failed_count = failed
    campaign.executed_at = datetime.utcnow()
    db.commit()
    db.refresh(campaign)
    user = get_or_create_default_user(db)
    log_activity(
        db,
        user.id,
        event_type="campaign_execute",
        entity_type="campaign",
        entity_id=str(campaign.id),
        details={"sent": sent, "failed": failed},
    )
    return APIResponse(
        success=True,
        data=CampaignExecutionResult(campaign_id=str(campaign.id), sent=sent, failed=failed, retried=campaign.retry_count),
        message="Campaign executed",
    )


@router.get("/{campaign_id}/logs", response_model=APIResponse[list[dict]])
async def campaign_logs(campaign_id: uuid.UUID, db: Session = Depends(get_db)) -> APIResponse[list[dict]]:
    rows = (
        db.query(OutreachStatusDB)
        .filter(OutreachStatusDB.campaign_id == campaign_id)
        .order_by(OutreachStatusDB.created_at.desc())
        .all()
    )
    return APIResponse(
        success=True,
        data=[
            {
                "id": str(row.id),
                "recipient_email": row.recipient_email,
                "status": row.status,
                "message_id": row.message_id,
                "error_message": row.error_message,
                "sent_at": row.sent_at.isoformat() if row.sent_at else None,
                "created_at": row.created_at.isoformat(),
            }
            for row in rows
        ],
    )


def _to_campaign(campaign: EmailCampaignDB) -> Campaign:
    return Campaign(
        id=campaign.id,
        user_id=str(campaign.user_id),
        name=campaign.name,
        status=campaign.status,
        total_drafts=campaign.total_drafts,
        sent_count=campaign.sent_count,
        failed_count=campaign.failed_count,
        retry_count=campaign.retry_count,
        last_error=campaign.last_error,
        executed_at=campaign.executed_at,
        created_at=campaign.created_at,
        updated_at=campaign.updated_at,
    )


async def _send_message(
    gmail_address: str,
    gmail_app_password: str,
    recipient: str | None,
    subject: str,
    body: str,
) -> str:
    if not recipient:
        raise ValueError("Recipient email is missing")

    message = MIMEText(body)
    message["From"] = gmail_address
    message["To"] = recipient
    message["Subject"] = subject

    def _send() -> str:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as smtp:
            smtp.login(gmail_address, gmail_app_password)
            result = smtp.send_message(message)
            return str(result) if result else "sent"

    return await asyncio.get_event_loop().run_in_executor(None, _send)
