from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger
from app.core.exceptions import setup_exception_handlers
from app.api.v1 import api_router
from app.core.db import get_engine
from app.core.migrations import run_safe_migrations
from app.models import db_models  # noqa: F401

logger = get_logger(__name__)

def create_app() -> FastAPI:
    """
    App factory pattern to create and configure the FastAPI application.
    
    Returns:
        A configured FastAPI application instance.
    """
    settings = get_settings()
    
    # Initialize logging
    setup_logging(debug=settings.DEBUG)
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    @app.get("/")
    def root():
        return {
            "status": "ok",
            "service": "Research Internship Agent",
        }

    @app.get("/health")
    def health():
        return {"status": "healthy"}

    @app.on_event("startup")
    def initialize_database() -> None:
        try:
            os.makedirs(settings.DATA_DIR, exist_ok=True)
            os.makedirs(settings.DOCUMENTS_DIR, exist_ok=True)
            run_safe_migrations(get_engine())
            logger.info("Database tables and migrations are ready")
        except Exception as exc:
            logger.error(f"Database initialization failed: {exc}")
    
    # Register exception handlers
    setup_exception_handlers(app)
    
    # Configure CORS
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_origin_regex=settings.BACKEND_CORS_ORIGIN_REGEX,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    # Register API routers
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    logger.info(f"Application '{settings.PROJECT_NAME}' initialized")
    
    return app
