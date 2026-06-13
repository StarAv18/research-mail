import uuid
from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    Uuid,
)
from app.core.db import Base
from app.models.draft import DraftStatus


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255))
    university = Column(String(255))
    bio = Column(Text)
    skills = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProfessorDB(Base):
    __tablename__ = "professors"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    university = Column(String(200), nullable=False)
    department = Column(String(100))
    email = Column(String(255))
    website = Column(String(500))
    country = Column(String(100))
    research_interests = Column(JSON, default=list)
    recent_publications = Column(JSON, default=list)
    biography = Column(Text)
    source = Column(String(50), default="search")
    source_metadata = Column(JSON, default=dict)
    last_scraped_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ResearchProfileDB(Base):
    __tablename__ = "research_profiles"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    professor_id = Column(Uuid, ForeignKey("professors.id"), nullable=False)
    summary = Column(Text)
    website_content = Column(Text)
    institution = Column(String(255))
    country = Column(String(100))
    research_interests = Column(JSON, default=list)
    recent_publications = Column(JSON, default=list)
    source = Column(String(50), default="discovery")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PublicationDB(Base):
    __tablename__ = "publications"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    professor_id = Column(Uuid, ForeignKey("professors.id"), nullable=False)
    title = Column(String(500), nullable=False)
    publication_year = Column(Integer)
    url = Column(String(500))
    abstract = Column(Text)
    source = Column(String(50), default="openalex")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmailCampaignDB(Base):
    __tablename__ = "email_campaigns"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="draft")
    total_drafts = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    retry_count = Column(Integer, default=0)
    last_error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    executed_at = Column(DateTime)


class EmailDraftDB(Base):
    __tablename__ = "email_drafts"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    professor_id = Column(Uuid, ForeignKey("professors.id"))
    user_id = Column(Uuid, ForeignKey("users.id"))
    campaign_id = Column(Uuid, ForeignKey("email_campaigns.id"))
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    status = Column(SQLEnum(DraftStatus), default=DraftStatus.PENDING)
    gmail_draft_id = Column(String(255))
    personalization_notes = Column(Text)
    source_context = Column(JSON, default=dict)
    current_version = Column(Integer, default=1)
    version_count = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DraftVersionDB(Base):
    __tablename__ = "email_draft_versions"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    draft_id = Column(Uuid, ForeignKey("email_drafts.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    editor = Column(String(100), default="system")
    change_reason = Column(String(255), default="initial")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DocumentDB(Base):
    __tablename__ = "documents"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    storage_path = Column(String(500), nullable=False)
    size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    extracted_text = Column(Text)
    metadata_json = Column(JSON, default=dict)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class OutreachStatusDB(Base):
    __tablename__ = "outreach_status"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    professor_id = Column(Uuid, ForeignKey("professors.id"))
    draft_id = Column(Uuid, ForeignKey("email_drafts.id"))
    campaign_id = Column(Uuid, ForeignKey("email_campaigns.id"))
    recipient_email = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="queued")
    provider = Column(String(50), default="gmail")
    message_id = Column(String(255))
    error_message = Column(Text)
    retries = Column(Integer, default=0)
    response_received = Column(Boolean, default=False)
    sent_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ActivityLogDB(Base):
    __tablename__ = "activity_logs"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey("users.id"), nullable=False)
    event_type = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(100))
    details = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SearchHistoryDB(Base):
    __tablename__ = "search_history"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey("users.id"), nullable=False)
    query = Column(String(500), nullable=False)
    research_area = Column(String(255))
    institution = Column(String(255))
    country = Column(String(100))
    region = Column(String(100))
    results_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserCredentialsDB(Base):
    __tablename__ = "user_credentials"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text)
    token_uri = Column(String(255), nullable=False)
    client_id = Column(String(255), nullable=False)
    client_secret = Column(String(255), nullable=False)
    scopes = Column(JSON, default=list)
    expiry = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


DraftDB = EmailDraftDB
