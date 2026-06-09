from app.services.ai.base import BaseHTTPProvider
from app.core.logging import get_logger

logger = get_logger(__name__)

class GeminiProvider(BaseHTTPProvider):
    """
    AI provider implementation for Google Gemini API.
    """

    @property
    def name(self) -> str:
        return f"gemini/{self.model}"

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash", timeout: float = 60.0):
        super().__init__(timeout=timeout)
        self.api_key = api_key
        self.model = model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    async def generate(self, prompt: str) -> str:
        """
        Generate a response using Gemini's generateContent API.
        """
        url = f"{self.base_url}?key={self.api_key}"
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        data = await self._request("POST", url, json_data=payload)
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected response structure from Gemini: {data}")
            return "Error: Received malformed response from Gemini."
