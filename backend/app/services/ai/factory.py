from typing import Optional
from fastapi import Depends
from app.core.config import Settings, get_settings
from app.models.enums import AIProvider
from app.services.ai.base import BaseAIProvider
from app.services.ai.ollama import OllamaProvider
from app.services.ai.openrouter import OpenRouterProvider
from app.services.ai.gemini import GeminiProvider
from app.services.ai.exceptions import AIConfigurationError

def get_ai_provider(
    provider_type: Optional[AIProvider] = None,
    settings: Settings = Depends(get_settings)
) -> BaseAIProvider:
    """
    Dependency injection factory for AI providers.
    
    Args:
        provider_type: The type of AI provider requested. Defaults to setting.
        settings: Application settings.
        
    Returns:
        An instance of a concrete BaseAIProvider.
    """
    # Use default from settings if not provided
    active_provider = provider_type or AIProvider(settings.DEFAULT_AI_PROVIDER)
    
    if active_provider == AIProvider.OPENROUTER:
        if not settings.OPENROUTER_API_KEY:
            raise AIConfigurationError("OPENROUTER_API_KEY is not set")
        return OpenRouterProvider(
            api_key=settings.OPENROUTER_API_KEY,
            model=settings.OPENROUTER_MODEL,
            timeout=settings.AI_TIMEOUT
        )
        
    elif active_provider == AIProvider.GEMINI:
        if not settings.GEMINI_API_KEY:
            raise AIConfigurationError("GEMINI_API_KEY is not set")
        return GeminiProvider(
            api_key=settings.GEMINI_API_KEY,
            model=settings.GEMINI_MODEL,
            timeout=settings.AI_TIMEOUT
        )
        
    elif active_provider == AIProvider.OLLAMA:
        return OllamaProvider(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            timeout=settings.AI_TIMEOUT
        )
        
    raise AIConfigurationError(f"Unsupported AI provider: {active_provider}")
