class AIProviderError(Exception):
    """Base exception for all AI provider errors."""
    pass

class AIConfigurationError(AIProviderError):
    """Raised when a provider is misconfigured (e.g., missing API keys)."""
    pass

class AIGenerationError(AIProviderError):
    """Raised when generation fails due to API errors or timeouts."""
    pass

class AIRateLimitError(AIProviderError):
    """Raised when hitting provider rate limits."""
    pass
