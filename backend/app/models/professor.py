from pydantic import Field, HttpUrl, EmailStr
from typing import List, Optional
from app.models.base import TimestampedModel

class Professor(TimestampedModel):
    """
    Represents a university professor or researcher.
    
    Inherits from TimestampedModel to support persistence and tracking.
    """
    name: str = Field(
        ..., 
        description="Full name of the professor", 
        min_length=2,
        max_length=100,
        examples=["Dr. Jane Smith"]
    )
    university: str = Field(
        ..., 
        description="Affiliated university or institution",
        max_length=200,
        examples=["Stanford University"]
    )
    department: Optional[str] = Field(
        None, 
        description="Academic department",
        max_length=100
    )
    email: Optional[EmailStr] = Field(
        None, 
        description="Contact email address"
    )
    website: Optional[HttpUrl] = Field(
        None, 
        description="Personal or lab website URL"
    )
    research_interests: List[str] = Field(
        default_factory=list, 
        description="List of research areas or keywords"
    )
    biography: Optional[str] = Field(
        None, 
        description="Short professional biography or description", 
        max_length=5000
    )
