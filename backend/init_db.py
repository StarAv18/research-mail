from app.core.db import Base, get_engine
from app.models.db_models import (
    ActivityLogDB,
    DocumentDB,
    DraftVersionDB,
    EmailCampaignDB,
    EmailDraftDB,
    OutreachStatusDB,
    ProfessorDB,
    PublicationDB,
    ResearchProfileDB,
    SearchHistoryDB,
    UserCredentialsDB,
    UserDB,
)

def init_db():
    """
    Initialize the database by creating all tables defined in SQLAlchemy models.
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=get_engine())
    print("Database tables created successfully.")

if __name__ == "__main__":
    init_db()
