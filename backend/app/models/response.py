from typing import Any, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    """
    Standard API response wrapper.
    
    Attributes:
        success: Whether the request was successful.
        data: The actual payload.
        message: Optional message for the user.
        error: Optional error details.
    """
    success: bool
    data: T | None = None
    message: str | None = None
    error: str | None = None

class ErrorResponse(APIResponse[None]):
    """
    Standard error response.
    """
    success: bool = False
