from pydantic import Field
from typing import List
from app.models.base import TimestampedModel
from app.models.enums import RecommendationStatus

class CriteriaScore(TimestampedModel):
    """Represents a score for a specific matching criterion."""
    criterion: str = Field(..., description="Name of the criterion (e.g., 'Research Alignment')", max_length=100)
    score: int = Field(..., description="Score from 1 to 10", ge=1, le=10)
    reasoning: str = Field(..., description="Explanation for the score", max_length=1000)

class FitScore(TimestampedModel):
    """
    Calculates the alignment between a student and a professor's research.
    
    Attributes:
        overall_score: Weighted average score from 1 to 100.
        criteria_breakdown: List of scores for individual criteria.
        strengths: List of strong alignment points.
        weaknesses: List of potential gaps or misalignment points.
        recommendation: Final verdict or recommendation.
    """
    overall_score: int = Field(..., description="Weighted average score from 1 to 100", ge=0, le=100)
    criteria_breakdown: List[CriteriaScore] = Field(..., description="List of scores for individual criteria")
    strengths: List[str] = Field(default_factory=list, description="List of strong alignment points")
    weaknesses: List[str] = Field(default_factory=list, description="List of potential gaps or misalignment points")
    recommendation: RecommendationStatus = Field(..., description="Final verdict or recommendation")
