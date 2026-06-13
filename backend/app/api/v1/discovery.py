from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional, TypedDict
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

class SearchHit(TypedDict):
    url: str
    title: str
    snippet: str

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
    try:
        terms = [research_area, institution, country, region, "professor faculty research email"]
        query = " ".join(term.strip() for term in terms if term and term.strip())
        if not query:
            query = "computer science professor faculty research email"

        hits = await _search_web(query=query, limit=limit * 2)
        professors: list[ProfessorSearchResult] = []
        seen: set[str] = set()

        for hit in hits:
            if len(professors) >= limit:
                break
            url = hit["url"]
            if url in seen:
                continue
            seen.add(url)

            try:
                professor = await scraper.scrape(url)
            except Exception:
                professor = None

            if professor and (professor.name != "Unknown Name" or professor.email):
                biography = professor.biography or hit["snippet"]
                result = ProfessorSearchResult(
                    name=professor.name,
                    university=professor.university,
                    department=professor.department,
                    email=str(professor.email) if professor.email else None,
                    website=str(professor.website) if professor.website else url,
                    research_interests=_extract_interests(biography, research_area),
                    recent_work=_extract_recent_work(biography),
                    biography=biography[:1200],
                )
            else:
                name = _name_from_search_title(hit["title"])
                if not name:
                    continue
                result = ProfessorSearchResult(
                    name=name,
                    university=_university_from_query_or_url(institution, url),
                    email=None,
                    website=url,
                    research_interests=_extract_interests(hit["snippet"], research_area),
                    recent_work=hit["snippet"][:300],
                    biography=hit["snippet"][:1200],
                )
            professors.append(result)
            _upsert_professor(db, result)

        if len(professors) < limit:
            for result in await _search_openalex(research_area, institution, country, limit - len(professors)):
                professors.append(result)
                _upsert_professor(db, result)

        db.commit()
        data = ProfessorSearchResponse(query=query, count=len(professors), professors=professors)
        return APIResponse(success=True, data=data, message=f"Found {len(professors)} professor profiles")
    except Exception as exc:
        db.rollback()
        data = ProfessorSearchResponse(query=research_area or institution or "search", count=0, professors=[])
        return APIResponse(success=True, data=data, message=f"Search could not complete: {type(exc).__name__}: {exc}")

async def _search_web(query: str, limit: int) -> list[SearchHit]:
    urls = await _search_duckduckgo(query, limit)
    if len(urls) < limit:
        urls.extend(await _search_bing(query, limit - len(urls)))
    deduped: list[SearchHit] = []
    seen: set[str] = set()
    for hit in urls:
        if hit["url"] in seen:
            continue
        seen.add(hit["url"])
        deduped.append(hit)
        if len(deduped) >= limit:
            break
    return deduped

async def _search_duckduckgo(query: str, limit: int) -> list[SearchHit]:
    search_url = "https://html.duckduckgo.com/html/?" + urlencode({"q": query})
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            response = await client.get(search_url, headers=headers)
            response.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    urls: list[SearchHit] = []
    for link in soup.select("a.result__a"):
        href = link.get("href")
        if not href:
            continue
        parsed = parse_qs(urlparse(href).query)
        if "uddg" in parsed:
            href = unquote(parsed["uddg"][0])
        elif href.startswith("//"):
            href = "https:" + href
        elif href.startswith("/"):
            continue
        if any(blocked in href for blocked in ["duckduckgo.com", "facebook.com", "linkedin.com", "twitter.com"]):
            continue
        container = link.find_parent(class_="result")
        snippet_el = container.select_one(".result__snippet") if container else None
        urls.append({
            "url": href,
            "title": link.get_text(" ", strip=True),
            "snippet": snippet_el.get_text(" ", strip=True) if snippet_el else "",
        })
        if len(urls) >= limit:
            break
    return urls

async def _search_bing(query: str, limit: int) -> list[SearchHit]:
    search_url = "https://www.bing.com/search?" + urlencode({"q": query})
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            response = await client.get(search_url, headers=headers)
            response.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    urls: list[SearchHit] = []
    for item in soup.select("li.b_algo"):
        link = item.select_one("h2 a")
        if not link:
            continue
        href = link.get("href")
        if not href or not href.startswith("http"):
            continue
        if any(blocked in href for blocked in ["bing.com", "facebook.com", "linkedin.com", "twitter.com"]):
            continue
        snippet = item.select_one(".b_caption p")
        urls.append({
            "url": href,
            "title": link.get_text(" ", strip=True),
            "snippet": snippet.get_text(" ", strip=True) if snippet else "",
        })
        if len(urls) >= limit:
            break
    return urls

async def _search_openalex(
    research_area: str,
    institution: str,
    country: str,
    limit: int,
) -> list[ProfessorSearchResult]:
    if limit <= 0:
        return []

    headers = {"User-Agent": "research-mail/1.0 (mailto:research@example.com)"}
    institution_id: str | None = None
    institution_name = institution
    async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers=headers) as client:
        if institution:
            inst_response = await client.get(
                "https://api.openalex.org/institutions",
                params={"search": institution, "per-page": 1},
            )
            if inst_response.status_code == 200:
                inst_results = inst_response.json().get("results", [])
                if inst_results:
                    raw_institution_id = inst_results[0].get("id")
                    institution_id = raw_institution_id.rsplit("/", 1)[-1] if raw_institution_id else None
                    institution_name = inst_results[0].get("display_name") or institution

        filters = [f"default.search:{research_area or institution or 'research'}"]
        if institution_id:
            filters.append(f"institutions.id:{institution_id}")

        works_response = await client.get(
            "https://api.openalex.org/works",
            params={
                "filter": ",".join(filters),
                "per-page": max(limit * 4, 12),
                "sort": "cited_by_count:desc",
            },
        )
        if works_response.status_code != 200 and institution_id:
            works_response = await client.get(
                "https://api.openalex.org/works",
                params={
                    "filter": f"default.search:{research_area or institution or 'research'}",
                    "per-page": max(limit * 4, 12),
                    "sort": "cited_by_count:desc",
                },
            )
        if works_response.status_code != 200:
            return []

        return _professors_from_openalex_works(
            works_response.json().get("results", []),
            institution_id=institution_id,
            institution_name=institution_name,
            research_area=research_area,
            limit=limit,
        )

def _professors_from_openalex_works(
    works: list[dict],
    institution_id: str | None,
    institution_name: str,
    research_area: str,
    limit: int,
) -> list[ProfessorSearchResult]:
    by_author: dict[str, dict] = {}
    for work in works:
        title = work.get("display_name") or work.get("title") or ""
        if not title:
            continue
        topics = [
            topic.get("display_name")
            for topic in (work.get("topics") or [])[:4]
            if topic.get("display_name")
        ]
        if research_area:
            topics.insert(0, research_area.title())

        for authorship in work.get("authorships") or []:
            author = authorship.get("author") or {}
            author_name = author.get("display_name")
            author_id = author.get("id") or author_name
            if not author_name or _looks_like_group_author(author_name):
                continue

            institutions = authorship.get("institutions") or []
            matching_institutions = [
                inst for inst in institutions
                if not institution_id or institution_id in _openalex_institution_ids(inst)
            ]
            if institution_id and not matching_institutions:
                continue

            institution = matching_institutions[0] if matching_institutions else (institutions[0] if institutions else {})
            resolved_institution = institution.get("display_name") or institution_name or "Unknown Institution"
            raw_affiliations = " ".join(authorship.get("raw_affiliation_strings") or [])
            email = _extract_email(raw_affiliations)

            record = by_author.setdefault(author_id, {
                "name": author_name,
                "university": resolved_institution,
                "email": email,
                "website": author.get("id"),
                "topics": [],
                "works": [],
            })
            if email and not record["email"]:
                record["email"] = email
            record["topics"].extend(topics)
            record["works"].append(f"{title} ({work.get('publication_year', 'n.d.')})")

            if len(by_author) >= limit * 2:
                break
        if len(by_author) >= limit * 2:
            break

    results: list[ProfessorSearchResult] = []
    for record in by_author.values():
        topics = list(dict.fromkeys(item for item in record["topics"] if item))[:6]
        works_text = "; ".join(list(dict.fromkeys(record["works"]))[:3])
        results.append(ProfessorSearchResult(
            name=record["name"],
            university=record["university"],
            email=record["email"],
            website=record["website"],
            research_interests=topics,
            recent_work=works_text,
            biography=works_text,
        ))
        if len(results) >= limit:
            break
    return results

def _looks_like_group_author(name: str) -> bool:
    lowered = name.lower()
    return any(word in lowered for word in ["consortium", "collaboration", "group", "ieee", "robotics"])

def _extract_email(text: str) -> str | None:
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0).lower() if match else None

def _openalex_institution_ids(institution: dict) -> list[str]:
    values = [institution.get("id") or "", *(institution.get("lineage") or [])]
    return [value.rsplit("/", 1)[-1] for value in values if value]

async def _openalex_recent_work(client: httpx.AsyncClient, author_id: str) -> str:
    if not author_id:
        return ""
    response = await client.get(
        "https://api.openalex.org/works",
        params={
            "filter": f"authorships.author.id:{author_id}",
            "sort": "publication_date:desc",
            "per-page": 2,
        },
    )
    if response.status_code != 200:
        return ""
    titles = [
        work.get("display_name")
        for work in response.json().get("results", [])
        if work.get("display_name")
    ]
    return "; ".join(titles)

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

def _name_from_search_title(title: str) -> str | None:
    cleaned = re.sub(r"\s*[-|–].*$", "", title).strip()
    cleaned = re.sub(r"\b(Profile|Faculty|People|Directory|Research|Lab|Group)\b", "", cleaned, flags=re.I).strip()
    words = [word for word in cleaned.split() if word[:1].isupper() or "." in word]
    if len(words) >= 2:
        return " ".join(words[:4])
    return cleaned if len(cleaned.split()) >= 2 else None

def _university_from_query_or_url(institution: str, url: str) -> str:
    if institution:
        return institution
    domain_match = re.search(r"https?://(?:www\.)?([a-zA-Z0-9.-]+)", url)
    if not domain_match:
        return "Unknown University"
    return domain_match.group(1).split(".")[0].replace("-", " ").title()
