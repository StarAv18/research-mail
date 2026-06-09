import httpx
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from app.core.logging import get_logger
from app.services.ai.exceptions import AIGenerationError, AIRateLimitError

logger = get_logger(__name__)

class BaseAIProvider(ABC):
    """
    Abstract base class for all AI providers.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the AI provider."""
        pass

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate a response for the given prompt."""
        pass

class BaseHTTPProvider(BaseAIProvider):
    """
    Base class for AI providers that interact via HTTP APIs.
    
    Provides shared logic for client management, timeouts, and error handling.
    """

    def __init__(self, timeout: float = 60.0):
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def _request(
        self, 
        method: str, 
        url: str, 
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute an HTTP request with standardized error handling.
        """
        client = await self._get_client()
        try:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                params=params
            )
            
            if response.status_code == 429:
                raise AIRateLimitError(f"Rate limit exceeded for {url}")
                
            response.raise_for_status()
            return response.json()
            
        except httpx.TimeoutException:
            logger.error(f"Timeout while calling {url}")
            raise AIGenerationError(f"Provider timeout for {url}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} from {url}: {e.response.text}")
            raise AIGenerationError(f"Provider returned error: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error calling {url}: {str(e)}")
            raise AIGenerationError(f"Unexpected provider error: {str(e)}")

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
