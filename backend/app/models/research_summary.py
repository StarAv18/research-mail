from pydantic import Field
from typing import List, Optional
from app.models.base import TimestampedModel

class Publication(TimestampedModel):
    """Represents a research publication."""
    title: str = Field(..., description="Title of the publication", max_length=500)
    year: Optional[int] = Field(None, description="Year of publication", ge=1900)
    url: Optional[str] = Field(None, description="URL to the publication")

class ResearchSummary(TimestampedModel):
    """
    Summarizes the research profile of a professor.
    
    Attributes:
        professor_id: Reference to the Professor model.
        summary: High-level summary of the research.
        key_achievements: List of notable research contributions.
        recent_publications: List of recent or significant publications.
        active_projects: List of ongoing research projects.
    """
    professor_name: str = Field(..., description="Name of the professor this summary belongs to")
    summary: str = Field(..., description="High-level summary of the research", min_length=50, max_length=10000)
    key_achievements: List[str] = Field(default_factory=list, description="List of notable research contributions")
    recent_publications: List[Publication] = Field(default_factory=list, description="List of recent or significant publications")
    active_projects: List[str] = Field(default_factory=list, description="List of ongoing research projects")
