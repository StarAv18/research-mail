from app.core.db import engine, Base
from app.models.db_models import ProfessorDB, DraftDB, UserCredentialsDB

def init_db():
    """
    Initialize the database by creating all tables defined in SQLAlchemy models.
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

if __name__ == "__main__":
    init_db()
