from app.services.ai.base import BaseHTTPProvider
from app.core.logging import get_logger

logger = get_logger(__name__)

class OllamaProvider(BaseHTTPProvider):
    """
    AI provider implementation for Ollama (local LLM).
    """

    @property
    def name(self) -> str:
        return f"ollama/{self.model}"

    def __init__(self, base_url: str, model: str = "llama3", timeout: float = 60.0):
        super().__init__(timeout=timeout)
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def generate(self, prompt: str) -> str:
        """
        Generate a response using Ollama's generate API.
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        data = await self._request("POST", url, json_data=payload)
        return data.get("response", "").strip()
