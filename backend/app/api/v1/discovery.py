from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from urllib.parse import parse_qs, unquote, urlencode, urlparse
import httpx
import re
from bs4 import BeautifulSoup
from app.models.response import APIResponse
from app.models.professor import Professor
from app.models.db_models import ProfessorDB
from app.services.university_scraper import UniversityProfileScraper
from app.core.db import get_db
from app.api.deps import get_scraper_service

router = APIRouter()

class ProfessorSearchResult(BaseModel):
    name: str
    university: str
    department: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    research_interests: List[str] = []
    recent_work: str = ""
    biography: str = ""

class ProfessorSearchResponse(BaseModel):
    query: str
    count: int
    professors: List[ProfessorSearchResult]

@router.get("/scrape", response_model=APIResponse[Professor])
async def scrape_professor(
    url: str = Query(..., description="University profile URL"),
    scraper: UniversityProfileScraper = Depends(get_scraper_service)
) -> APIResponse[Professor]:
    """Scrape a professor profile from a university URL."""
    professor = await scraper.scrape(url)
    return APIResponse(success=True, data=professor, message="Professor profile extracted successfully")

@router.get("/search", response_model=APIResponse[ProfessorSearchResponse])
async def search_professors(
    research_area: str = Query("", description="Research area or topic"),
    institution: str = Query("", description="University or institute name"),
    country: str = Query("", description="Country"),
    region: str = Query("", description="Region or state"),
    limit: int = Query(8, ge=1, le=12),
    db: Session = Depends(get_db),
    scraper: UniversityProfileScraper = Depends(get_scraper_service),
) -> APIResponse[ProfessorSearchResponse]:
    """Search the public web for professor pages, scrape them, and persist found professors."""
    terms = [research_area, institution, country, region, "professor faculty research email"]
    query = " ".join(term.strip() for term in terms if term and term.strip())
    if not query:
        query = "computer science professor faculty research email"

    urls = await _search_web(query=query, limit=limit * 2)
    professors: list[ProfessorSearchResult] = []
    seen: set[str] = set()

    for url in urls:
        if len(professors) >= limit:
            break
        if url in seen:
            continue
        seen.add(url)

        try:
            professor = await scraper.scrape(url)
        except Exception:
            continue

        if professor.name == "Unknown Name" and not professor.email:
            continue

        biography = professor.biography or ""
        interests = _extract_interests(biography, research_area)
        recent_work = _extract_recent_work(biography)
        result = ProfessorSearchResult(
            name=professor.name,
            university=professor.university,
            department=professor.department,
            email=str(professor.email) if professor.email else None,
            website=str(professor.website) if professor.website else url,
            research_interests=interests,
            recent_work=recent_work,
            biography=biography[:1200],
        )
        professors.append(result)
        _upsert_professor(db, result)

    db.commit()
    data = ProfessorSearchResponse(query=query, count=len(professors), professors=professors)
    return APIResponse(success=True, data=data, message=f"Found {len(professors)} professor profiles")

async def _search_web(query: str, limit: int) -> list[str]:
    search_url = "https://html.duckduckgo.com/html/?" + urlencode({"q": query})
    headers = {"User-Agent": "Mozilla/5.0"}
    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        response = await client.get(search_url, headers=headers)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    urls: list[str] = []
    for link in soup.select("a.result__a"):
        href = link.get("href")
        if not href:
            continue
        if href.startswith("//"):
            href = "https:" + href
        if href.startswith("/"):
            parsed = parse_qs(urlparse(href).query)
            if "uddg" not in parsed:
                continue
            href = unquote(parsed["uddg"][0])
        if any(blocked in href for blocked in ["duckduckgo.com", "facebook.com", "linkedin.com", "twitter.com"]):
            continue
        urls.append(href)
        if len(urls) >= limit:
            break
    return urls

def _extract_interests(text: str, seed: str) -> list[str]:
    candidates = [
        "artificial intelligence", "machine learning", "deep learning", "computer vision",
        "natural language processing", "robotics", "data science", "bioinformatics",
        "systems", "security", "networks", "human-computer interaction", "databases",
        "algorithms", "theory", "software engineering", "health", "climate", "energy",
    ]
    lowered = text.lower()
    interests = [item.title() for item in candidates if item in lowered]
    if seed:
        interests.insert(0, seed.strip().title())
    return list(dict.fromkeys(interests))[:6]

def _extract_recent_work(text: str) -> str:
    snippets = []
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        lowered = sentence.lower()
        if any(word in lowered for word in ["publication", "published", "recent", "project", "research"]):
            cleaned = sentence.strip()
            if 40 <= len(cleaned) <= 260:
                snippets.append(cleaned)
        if len(snippets) == 2:
            break
    return " ".join(snippets) or text[:240]

def _upsert_professor(db: Session, professor: ProfessorSearchResult) -> None:
    existing = None
    if professor.email:
        existing = db.query(ProfessorDB).filter(ProfessorDB.email == professor.email).first()
    if not existing and professor.website:
        existing = db.query(ProfessorDB).filter(ProfessorDB.website == professor.website).first()

    if existing:
        existing.name = professor.name
        existing.university = professor.university
        existing.department = professor.department
        existing.website = professor.website
        existing.research_interests = professor.research_interests
        existing.biography = professor.biography
        return

    db.add(ProfessorDB(
        name=professor.name,
        university=professor.university,
        department=professor.department,
        email=professor.email,
        website=professor.website,
        research_interests=professor.research_interests,
        biography=professor.biography,
    ))
