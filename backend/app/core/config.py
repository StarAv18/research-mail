from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
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
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "https://research-internship-agent.vercel.app",
        "https://research-mail-zmt6-sandy.vercel.app",
    ]
    BACKEND_CORS_ORIGIN_REGEX: str = r"^https://.*\.vercel\.app$"

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "searchmail"
    SQLALCHEMY_DATABASE_URL: str | None = None

    @property
    def database_url(self) -> str:
        if self.SQLALCHEMY_DATABASE_URL:
            return self.SQLALCHEMY_DATABASE_URL
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/callback"
    
    # Storage
    DATA_DIR: str = "data"
    
    # AI Keys
    OPENROUTER_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    # AI Default Models
    DEFAULT_AI_PROVIDER: str = "ollama"
    OLLAMA_MODEL: str = "llama3"
    OPENROUTER_MODEL: str = "google/gemini-pro-1.5"
    GEMINI_MODEL: str = "gemini-1.5-flash"
    AI_TIMEOUT: float = 60.0
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    """
    return Settings()
