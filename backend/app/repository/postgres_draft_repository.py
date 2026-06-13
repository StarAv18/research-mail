from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.draft import Draft, DraftVersion
from app.models.db_models import DraftVersionDB, EmailDraftDB, ProfessorDB
from app.repository.draft_repository import DraftRepository
from app.services.platform_service import get_or_create_default_user

class PostgresDraftRepository(DraftRepository):
    """
    PostgreSQL implementation of DraftRepository using SQLAlchemy.
    """

    def __init__(self, db: Session):
        self.db = db

    def _to_pydantic(self, db_draft: EmailDraftDB, professor: ProfessorDB) -> Draft:
        """Helper to convert DB models to Pydantic Draft model."""
        return Draft(
            id=db_draft.id,
            professor_name=professor.name,
            professor_email=professor.email,
            university=professor.university,
            subject=db_draft.subject,
            body=db_draft.body,
            status=db_draft.status,
            personalization_notes=db_draft.personalization_notes,
            current_version=db_draft.current_version or 1,
            version_count=db_draft.version_count or 1,
            created_at=db_draft.created_at,
            updated_at=db_draft.updated_at,
        )

    def _version_to_pydantic(self, db_version: DraftVersionDB) -> DraftVersion:
        return DraftVersion(
            id=db_version.id,
            draft_id=str(db_version.draft_id),
            version_number=db_version.version_number,
            subject=db_version.subject,
            body=db_version.body,
            editor=db_version.editor,
            change_reason=db_version.change_reason,
            created_at=db_version.created_at,
            updated_at=db_version.updated_at,
        )

    async def create(self, entity: Draft) -> Draft:
        user = get_or_create_default_user(self.db)
        # Find or create professor
        professor = self.db.query(ProfessorDB).filter(ProfessorDB.email == entity.professor_email).first()
        if not professor:
            professor = ProfessorDB(
                name=entity.professor_name,
                email=entity.professor_email,
                university=entity.university,
            )
            self.db.add(professor)
            self.db.flush()

        db_draft = EmailDraftDB(
            professor_id=professor.id,
            user_id=user.id,
            subject=entity.subject,
            body=entity.body,
            status=entity.status,
            personalization_notes=entity.personalization_notes,
            current_version=entity.current_version or 1,
            version_count=entity.version_count or 1,
        )
        self.db.add(db_draft)
        self.db.flush()
        self.db.add(
            DraftVersionDB(
                draft_id=db_draft.id,
                version_number=db_draft.current_version or 1,
                subject=entity.subject,
                body=entity.body,
                editor="system",
                change_reason="initial",
            )
        )
        self.db.commit()
        self.db.refresh(db_draft)
        return self._to_pydantic(db_draft, professor)

    async def get_by_id(self, id: UUID) -> Optional[Draft]:
        result = (
            self.db.query(EmailDraftDB, ProfessorDB)
            .join(ProfessorDB)
            .filter(EmailDraftDB.id == id)
            .first()
        )
        if not result:
            return None
        db_draft, professor = result
        return self._to_pydantic(db_draft, professor)

    async def update(self, id: UUID, updated_entity: Draft) -> Draft:
        result = (
            self.db.query(EmailDraftDB, ProfessorDB)
            .join(ProfessorDB)
            .filter(EmailDraftDB.id == id)
            .first()
        )
        if not result:
            raise ValueError(f"Draft with ID {id} not found")
        
        db_draft, professor = result
        
        # Update professor if needed
        professor.name = updated_entity.professor_name
        professor.email = updated_entity.professor_email
        professor.university = updated_entity.university
        
        # Update draft
        db_draft.subject = updated_entity.subject
        db_draft.body = updated_entity.body
        db_draft.status = updated_entity.status
        db_draft.personalization_notes = updated_entity.personalization_notes
        db_draft.current_version = updated_entity.current_version or db_draft.current_version or 1
        db_draft.version_count = updated_entity.version_count or db_draft.version_count or 1
        
        self.db.commit()
        self.db.refresh(db_draft)
        self.db.refresh(professor)
        return self._to_pydantic(db_draft, professor)

    async def delete(self, id: UUID) -> bool:
        db_draft = self.db.query(EmailDraftDB).filter(EmailDraftDB.id == id).first()
        if not db_draft:
            return False
        self.db.query(DraftVersionDB).filter(DraftVersionDB.draft_id == id).delete()
        self.db.delete(db_draft)
        self.db.commit()
        return True

    async def list_all(self) -> List[Draft]:
        results = self.db.query(EmailDraftDB, ProfessorDB).join(ProfessorDB).all()
        return [self._to_pydantic(d, p) for d, p in results]

    async def search(self, query: str) -> List[Draft]:
        search_query = f"%{query.lower()}%"
        results = self.db.query(EmailDraftDB, ProfessorDB).join(ProfessorDB).filter(
            or_(
                ProfessorDB.name.ilike(search_query),
                ProfessorDB.university.ilike(search_query),
                ProfessorDB.email.ilike(search_query),
                EmailDraftDB.subject.ilike(search_query)
            )
        ).all()
        return [self._to_pydantic(d, p) for d, p in results]

    async def list_versions(self, id: UUID) -> List[DraftVersion]:
        versions = (
            self.db.query(DraftVersionDB)
            .filter(DraftVersionDB.draft_id == id)
            .order_by(DraftVersionDB.version_number.desc())
            .all()
        )
        return [self._version_to_pydantic(version) for version in versions]

    async def save_version(
        self,
        id: UUID,
        subject: str,
        body: str,
        editor: str = "system",
        change_reason: str = "manual update",
    ) -> Draft:
        result = (
            self.db.query(EmailDraftDB, ProfessorDB)
            .join(ProfessorDB)
            .filter(EmailDraftDB.id == id)
            .first()
        )
        if not result:
            raise ValueError(f"Draft with ID {id} not found")

        db_draft, professor = result
        next_version = (db_draft.version_count or 1) + 1
        db_draft.subject = subject
        db_draft.body = body
        db_draft.current_version = next_version
        db_draft.version_count = next_version
        self.db.add(
            DraftVersionDB(
                draft_id=db_draft.id,
                version_number=next_version,
                subject=subject,
                body=body,
                editor=editor,
                change_reason=change_reason,
            )
        )
        self.db.commit()
        self.db.refresh(db_draft)
        return self._to_pydantic(db_draft, professor)
