from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine
from app.core.logging import get_logger
from app.models import db_models  # noqa: F401
from app.core.db import Base

logger = get_logger(__name__)


def _add_column_if_missing(engine: Engine, table_name: str, column_name: str, ddl: str) -> None:
    inspector = inspect(engine)
    if not inspector.has_table(table_name):
        return
    existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
    if column_name in existing_columns:
        return
    with engine.begin() as connection:
        connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {ddl}"))
    logger.info("Added missing column %s.%s", table_name, column_name)


def _rename_legacy_drafts_table(engine: Engine) -> None:
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    if "drafts" in tables and "email_drafts" not in tables:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE drafts RENAME TO email_drafts"))
        logger.info("Renamed legacy drafts table to email_drafts")


def run_safe_migrations(engine: Engine) -> None:
    """
    Apply additive schema changes without destroying existing production data.
    """
    _rename_legacy_drafts_table(engine)
    Base.metadata.create_all(bind=engine)

    dialect = engine.dialect.name
    if dialect == "postgresql":
        _add_column_if_missing(engine, "professors", "country", "country VARCHAR(100)")
        _add_column_if_missing(engine, "professors", "recent_publications", "recent_publications JSON")
        _add_column_if_missing(engine, "professors", "source", "source VARCHAR(50) DEFAULT 'search'")
        _add_column_if_missing(engine, "professors", "source_metadata", "source_metadata JSON")
        _add_column_if_missing(engine, "professors", "last_scraped_at", "last_scraped_at TIMESTAMP")
        _add_column_if_missing(engine, "email_drafts", "user_id", "user_id UUID")
        _add_column_if_missing(engine, "email_drafts", "campaign_id", "campaign_id UUID")
        _add_column_if_missing(engine, "email_drafts", "personalization_notes", "personalization_notes TEXT")
        _add_column_if_missing(engine, "email_drafts", "source_context", "source_context JSON")
        _add_column_if_missing(engine, "email_drafts", "current_version", "current_version INTEGER DEFAULT 1")
        _add_column_if_missing(engine, "email_drafts", "version_count", "version_count INTEGER DEFAULT 1")
    elif dialect == "sqlite":
        _add_column_if_missing(engine, "professors", "country", "country TEXT")
        _add_column_if_missing(engine, "professors", "recent_publications", "recent_publications JSON")
        _add_column_if_missing(engine, "professors", "source", "source TEXT DEFAULT 'search'")
        _add_column_if_missing(engine, "professors", "source_metadata", "source_metadata JSON")
        _add_column_if_missing(engine, "professors", "last_scraped_at", "last_scraped_at DATETIME")
        _add_column_if_missing(engine, "email_drafts", "user_id", "user_id TEXT")
        _add_column_if_missing(engine, "email_drafts", "campaign_id", "campaign_id TEXT")
        _add_column_if_missing(engine, "email_drafts", "personalization_notes", "personalization_notes TEXT")
        _add_column_if_missing(engine, "email_drafts", "source_context", "source_context JSON")
        _add_column_if_missing(engine, "email_drafts", "current_version", "current_version INTEGER DEFAULT 1")
        _add_column_if_missing(engine, "email_drafts", "version_count", "version_count INTEGER DEFAULT 1")
