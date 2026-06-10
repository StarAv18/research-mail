from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger
from app.core.exceptions import setup_exception_handlers
from app.api.v1 import api_router

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
    
    # Register exception handlers
    setup_exception_handlers(app)
    
    # Configure CORS
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    # Register API routers
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    logger.info(f"Application '{settings.PROJECT_NAME}' initialized")
    
    return app
