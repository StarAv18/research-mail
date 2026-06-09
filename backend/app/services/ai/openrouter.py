from app.services.ai.base import BaseHTTPProvider
from app.core.logging import get_logger

logger = get_logger(__name__)

class OpenRouterProvider(BaseHTTPProvider):
    """
    AI provider implementation for OpenRouter API.
    """

    @property
    def name(self) -> str:
        return f"openrouter/{self.model}"

    def __init__(self, api_key: str, model: str = "google/gemini-pro-1.5", timeout: float = 60.0):
        super().__init__(timeout=timeout)
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    async def generate(self, prompt: str) -> str:
        """
        Generate a response using OpenRouter's chat completions API.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/internship-agent",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}]
        }

        data = await self._request("POST", self.base_url, headers=headers, json_data=payload)
        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected response structure from OpenRouter: {data}")
            return "Error: Received malformed response from OpenRouter."
