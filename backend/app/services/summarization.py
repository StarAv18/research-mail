import json
from typing import Any, Dict
from app.models.research_summary import ResearchSummary
from app.services.ai.base import BaseAIProvider
from app.core.logging import get_logger
from app.services.ai.exceptions import AIGenerationError
from app.core.prompts import SUMMARIZATION_PROMPT
from app.core.utils import parse_ai_json

logger = get_logger(__name__)

class SummarizationService:
    """
    Service for generating structured research summaries from raw text using AI.
    """

    def __init__(self, ai_provider: BaseAIProvider):
        self.ai_provider = ai_provider

    async def summarize(self, professor_name: str, research_text: str) -> ResearchSummary:
        output_format = {
            "summary": "Professional summary (string, min 50 chars)",
            "key_achievements": ["List of strings"],
            "recent_publications": [
                {"title": "string", "year": "integer", "url": "string (optional)"}
            ],
            "active_projects": ["List of strings"]
        }

        prompt = SUMMARIZATION_PROMPT.format(
            research_text=research_text,
            output_format=json.dumps(output_format, indent=2)
        )
        
        try:
            raw_response = await self.ai_provider.generate(prompt)
            structured_data = parse_ai_json(raw_response)
            structured_data["professor_name"] = professor_name
            return ResearchSummary(**structured_data)
        except Exception as e:
            logger.error(f"Summarization error for {professor_name}: {str(e)}")
            raise AIGenerationError(f"Failed to generate summary: {str(e)}")
