from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.draft import Draft
from app.models.db_models import DraftDB, ProfessorDB
from app.repository.draft_repository import DraftRepository

class PostgresDraftRepository(DraftRepository):
    """
    PostgreSQL implementation of DraftRepository using SQLAlchemy.
    """

    def __init__(self, db: Session):
        self.db = db

    def _to_pydantic(self, db_draft: DraftDB, professor: ProfessorDB) -> Draft:
        """Helper to convert DB models to Pydantic Draft model."""
        return Draft(
            id=db_draft.id,
            professor_name=professor.name,
            professor_email=professor.email,
            university=professor.university,
            subject=db_draft.subject,
            body=db_draft.body,
            status=db_draft.status,
            created_at=db_draft.created_at,
            updated_at=db_draft.updated_at
        )

    async def create(self, entity: Draft) -> Draft:
        # Find or create professor
        professor = self.db.query(ProfessorDB).filter(ProfessorDB.email == entity.professor_email).first()
        if not professor:
            professor = ProfessorDB(
                name=entity.professor_name,
                email=entity.professor_email,
                university=entity.university
            )
            self.db.add(professor)
            self.db.flush() # Get ID without committing

        db_draft = DraftDB(
            professor_id=professor.id,
            subject=entity.subject,
            body=entity.body,
            status=entity.status
        )
        self.db.add(db_draft)
        self.db.commit()
        self.db.refresh(db_draft)
        return self._to_pydantic(db_draft, professor)

    async def get_by_id(self, id: UUID) -> Optional[Draft]:
        result = self.db.query(DraftDB, ProfessorDB).join(ProfessorDB).filter(DraftDB.id == id).first()
        if not result:
            return None
        db_draft, professor = result
        return self._to_pydantic(db_draft, professor)

    async def update(self, id: UUID, updated_entity: Draft) -> Draft:
        result = self.db.query(DraftDB, ProfessorDB).join(ProfessorDB).filter(DraftDB.id == id).first()
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
        
        self.db.commit()
        self.db.refresh(db_draft)
        self.db.refresh(professor)
        return self._to_pydantic(db_draft, professor)

    async def delete(self, id: UUID) -> bool:
        db_draft = self.db.query(DraftDB).filter(DraftDB.id == id).first()
        if not db_draft:
            return False
        self.db.delete(db_draft)
        self.db.commit()
        return True

    async def list_all(self) -> List[Draft]:
        results = self.db.query(DraftDB, ProfessorDB).join(ProfessorDB).all()
        return [self._to_pydantic(d, p) for d, p in results]

    async def search(self, query: str) -> List[Draft]:
        search_query = f"%{query.lower()}%"
        results = self.db.query(DraftDB, ProfessorDB).join(ProfessorDB).filter(
            or_(
                ProfessorDB.name.ilike(search_query),
                ProfessorDB.university.ilike(search_query),
                ProfessorDB.email.ilike(search_query),
                DraftDB.subject.ilike(search_query)
            )
        ).all()
        return [self._to_pydantic(d, p) for d, p in results]
