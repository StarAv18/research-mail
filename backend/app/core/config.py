from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    """
    Application settings and environment variables.
    
    Attributes:
        PROJECT_NAME: Name of the project.
        API_V1_STR: API version string.
        SECRET_KEY: Secret key for security.
        DEBUG: Debug mode flag.
        OPENROUTER_API_KEY: API key for OpenRouter.
        GEMINI_API_KEY: API key for Gemini.
        OLLAMA_BASE_URL: Base URL for Ollama.
    """
    PROJECT_NAME: str = "Research Internship Agent"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "development-secret-key"
    DEBUG: bool = True
    
    # AI Keys
    OPENROUTER_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    """
    return Settings()
