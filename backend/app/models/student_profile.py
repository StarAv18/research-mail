from pydantic import Field, EmailStr
from typing import List, Optional
from app.models.base import TimestampedModel

class StudentProfile(TimestampedModel):
    """
    Represents the profile of a student applying for research internships.
    
    Attributes:
        full_name: Student's full name.
        email: Contact email address.
        university: Current university.
        major: Field of study.
        gpa: Current GPA.
        skills: List of technical or research skills.
        experience: Summary of relevant research or work experience.
        interests: Key research areas of interest.
        resume_url: Optional link to a hosted resume.
    """
    full_name: str = Field(..., description="Student's full name", min_length=2)
    email: EmailStr = Field(..., description="Student's contact email")
    university: str = Field(..., description="Current university name")
    major: str = Field(..., description="Field of study")
    gpa: Optional[float] = Field(None, description="Current GPA", ge=0, le=4.0)
    skills: List[str] = Field(default_factory=list, description="List of technical or research skills")
    experience: str = Field(..., description="Summary of relevant research or work experience", min_length=50)
    interests: List[str] = Field(default_factory=list, description="Key research areas of interest")
    resume_url: Optional[str] = Field(None, description="Optional link to a hosted resume")
