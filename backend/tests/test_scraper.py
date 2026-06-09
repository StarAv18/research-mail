import pytest
from unittest.mock import MagicMock
from app.services.university_scraper import UniversityProfileScraper
from app.models.professor import Professor

def test_scraper_extracts_data_correctly():
    """Test that the scraper correctly parses HTML content."""
    # Mock HTML content
    mock_html = """
    <html>
        <head><title>Dr. John Doe | Stanford University</title></head>
        <body>
            <h1>Dr. John Doe</h1>
            <p>Email: john.doe@stanford.edu</p>
            <a href="http://doe-lab.stanford.edu">Lab Website</a>
            <h2>Research Interests</h2>
            <p>Artificial Intelligence and Machine Learning.</p>
            <p>Computer Vision and Robotics.</p>
        </body>
    </html>
    """
    
    # Mock requests session
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.text = mock_html
    mock_response.status_code = 200
    mock_session.get.return_value = mock_response
    
    scraper = UniversityProfileScraper(session=mock_session)
    professor = scraper.scrape("https://profiles.stanford.edu/john-doe")
    
    assert isinstance(professor, Professor)
    assert professor.name == "Dr. John Doe"
    assert str(professor.email) == "john.doe@stanford.edu"
    assert "Artificial Intelligence" in professor.biography
    assert "Computer Vision" in professor.biography
    assert str(professor.website).rstrip("/") == "http://doe-lab.stanford.edu"

def test_scraper_handles_missing_email():
    """Test that the scraper handles cases where no email is found."""
    mock_html = "<html><body><h1>No Email Prof</h1><p>Some research text.</p></body></html>"
    
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.text = mock_html
    mock_response.status_code = 200
    mock_session.get.return_value = mock_response
    
    scraper = UniversityProfileScraper(session=mock_session)
    professor = scraper.scrape("https://example.edu/prof")
    
    assert professor.name == "No Email Prof"
    assert professor.email is None
