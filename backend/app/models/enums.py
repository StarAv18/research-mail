from enum import Enum

class AIProvider(str, Enum):
    """Supported AI Providers."""
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"
    GEMINI = "gemini"

class RecommendationStatus(str, Enum):
    """Final recommendation status for a professor match."""
    HIGHLY_RECOMMENDED = "Highly Recommended"
    RECOMMENDED = "Recommended"
    POTENTIAL_MATCH = "Potential Match"
    NOT_RECOMMENDED = "Not Recommended"
