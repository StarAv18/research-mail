import json
from typing import Any, Dict, Optional
from app.models.professor import Professor
from app.models.student_profile import StudentProfile
from app.models.research_summary import ResearchSummary
from app.models.generated_email import GeneratedEmail
from app.services.ai.base import BaseAIProvider
from app.services.ai.exceptions import AIGenerationError
from app.core.prompts import EMAIL_GENERATION_PROMPT
from app.core.utils import parse_ai_json
from app.core.logging import get_logger

logger = get_logger(__name__)

class EmailGenerationService:
    """
    Service for generating personalized outreach emails using AI.
    """

    def __init__(self, ai_provider: BaseAIProvider):
        self.ai_provider = ai_provider

    async def generate_email(
        self, 
        professor: Professor, 
        research_summary: ResearchSummary,
        student: StudentProfile,
        email_style: str = "Standard Professional"
    ) -> GeneratedEmail:
        prompt = EMAIL_GENERATION_PROMPT.format(
            professor_name=professor.name,
            professor_university=professor.university,
            professor_interests=", ".join(professor.research_interests),
            professor_summary=research_summary.summary,
            student_name=student.full_name,
            student_university=student.university,
            student_major=student.major,
            student_skills=", ".join(student.skills),
            student_experience=student.experience,
            student_interests=", ".join(student.interests),
            email_style=email_style
        )

        try:
            raw_response = await self.ai_provider.generate(prompt)
            structured_data = parse_ai_json(raw_response)
            
            return GeneratedEmail(
                subject=structured_data["subject"],
                body=structured_data["body"],
                recipient_name=professor.name,
                provider_used=self.ai_provider.name
            )
            
        except Exception as e:
            logger.error(f"Email generation failed for {professor.name}: {str(e)}")
            raise AIGenerationError(f"Failed to generate email: {str(e)}")
