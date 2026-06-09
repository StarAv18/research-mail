import pytest
from unittest.mock import AsyncMock
from app.services.summarization import SummarizationService
from app.models.research_summary import ResearchSummary

@pytest.mark.asyncio
async def test_summarization_service_success():
    """Test successful summarization and parsing."""
    mock_ai = AsyncMock()
    mock_ai.generate.return_value = """
    {
        "professor_name": "Dr. Smith",
        "summary": "This is a long enough summary to pass the 50 character validation requirement for the model.",
        "key_achievements": ["Won a Nobel Prize", "Published 1000 papers"],
        "recent_publications": [
            {
                "title": "AI in 2024",
                "year": 2024,
                "url": "http://example.com"
            }
        ],
        "active_projects": ["Deep Learning Foundations"]
    }
    """
    
    service = SummarizationService(ai_provider=mock_ai)
    result = await service.summarize("Dr. Smith", "Raw research text content...")
    
    assert isinstance(result, ResearchSummary)
    assert result.professor_name == "Dr. Smith"
    assert len(result.key_achievements) == 2
    assert result.recent_publications[0].year == 2024

@pytest.mark.asyncio
async def test_summarization_service_json_extraction():
    """Test that the service can extract JSON from wrapped AI responses."""
    mock_ai = AsyncMock()
    # AI response wrapped in conversational text and markdown
    mock_ai.generate.return_value = """
    Certainly! Here is the structured summary for the professor:

    ```json
    {
        "summary": "This is a long enough summary to pass the 50 character validation requirement for the model.",
        "key_achievements": [],
        "recent_publications": [],
        "active_projects": []
    }
    ```

    Let me know if you need anything else!
    """
    
    service = SummarizationService(ai_provider=mock_ai)
    result = await service.summarize("Dr. Smith", "Raw content")
    
    assert isinstance(result, ResearchSummary)
    assert result.professor_name == "Dr. Smith"
    assert "validation requirement" in result.summary
