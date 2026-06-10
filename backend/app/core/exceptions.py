from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.models.response import ErrorResponse
from app.core.logging import get_logger
from app.services.ai.exceptions import AIConfigurationError, AIGenerationError

logger = get_logger(__name__)

def setup_exception_handlers(app: FastAPI) -> None:
    """
    Register global exception handlers for the application.
    
    Args:
        app: The FastAPI application instance.
    """
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """Handle HTTP exceptions."""
        logger.error(f"HTTP error: {exc.detail} at {request.url}")
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                success=False,
                error=exc.detail,
                message="An HTTP error occurred"
            ).model_dump()
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Handle validation errors."""
        logger.error(f"Validation error: {exc.errors()} at {request.url}")
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                success=False,
                error=str(exc.errors()),
                message="Data validation failed"
            ).model_dump()
        )

    @app.exception_handler(AIConfigurationError)
    async def ai_configuration_handler(request: Request, exc: AIConfigurationError) -> JSONResponse:
        """Return useful errors when the user has not configured an AI key."""
        logger.error(f"AI configuration error: {str(exc)} at {request.url}")
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                success=False,
                error=str(exc),
                message="AI provider is not configured"
            ).model_dump()
        )

    @app.exception_handler(AIGenerationError)
    async def ai_generation_handler(request: Request, exc: AIGenerationError) -> JSONResponse:
        """Return useful errors for AI provider failures."""
        logger.error(f"AI generation error: {str(exc)} at {request.url}")
        return JSONResponse(
            status_code=502,
            content=ErrorResponse(
                success=False,
                error=str(exc),
                message="AI provider request failed"
            ).model_dump()
        )

    @app.exception_handler(Exception)
    async def universal_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle all other unhandled exceptions."""
        logger.exception(f"Unhandled exception: {str(exc)} at {request.url}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                success=False,
                error="Internal Server Error",
                message="An unexpected error occurred on the server"
            ).model_dump()
        )
