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
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
    )
    
    # Register exception handlers
    setup_exception_handlers(app)
    
    # Configure CORS
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    # Register API routers
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    logger.info(f"Application '{settings.PROJECT_NAME}' initialized")
    
    return app
