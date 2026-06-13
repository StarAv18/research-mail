from datetime import datetime
import re
from typing import List, Optional, TypedDict
from urllib.parse import parse_qs, unquote, urlencode, urlparse

import httpx
from bs4 import BeautifulSoup
from fastapi import APIRouter, Body, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_scraper_service
from app.core.config import get_settings
from app.core.db import get_db
from app.models.db_models import ProfessorDB, PublicationDB, ResearchProfileDB
from app.models.professor import Professor
from app.models.response import APIResponse
from app.services.platform_service import get_or_create_default_user, log_activity, record_search
from app.services.university_scraper import UniversityProfileScraper

router = APIRouter()
DISCOVERY_ENGINE_VERSION = "works-v5"


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
    country: Optional[str] = None
    research_interests: List[str] = []
    recent_publications: List[str] = []
    recent_work: str = ""
    biography: str = ""


class ProfessorSearchResponse(BaseModel):
    query: str
    count: int
    page: int = 1
    limit: int = 10
    professors: List[ProfessorSearchResult]


class ScrapeRequest(BaseModel):
    url: str


@router.get("/scrape", response_model=APIResponse[Professor])
async def scrape_professor(
    url: str = Query(..., description="University profile URL"),
    db: Session = Depends(get_db),
    scraper: UniversityProfileScraper = Depends(get_scraper_service),
) -> APIResponse[Professor]:
    professor = await scraper.scrape(url)
    persisted = _save_scraped_professor(db, professor, url)
    user = get_or_create_default_user(db)
    log_activity(
        db,
        user.id,
        event_type="scrape",
        entity_type="professor",
        entity_id=str(persisted.id),
        details={"url": url, "name": persisted.name},
    )
    return APIResponse(success=True, data=persisted, message="Professor profile extracted successfully")


@router.post("/scrape", response_model=APIResponse[Professor])
async def scrape_professor_post(
    request: ScrapeRequest = Body(...),
    db: Session = Depends(get_db),
    scraper: UniversityProfileScraper = Depends(get_scraper_service),
) -> APIResponse[Professor]:
    professor = await scraper.scrape(request.url)
    persisted = _save_scraped_professor(db, professor, request.url)
    user = get_or_create_default_user(db)
    log_activity(
        db,
        user.id,
        event_type="scrape",
        entity_type="professor",
        entity_id=str(persisted.id),
        details={"url": request.url, "name": persisted.name},
    )
    return APIResponse(success=True, data=persisted, message="Professor profile extracted successfully")


@router.get("/search", response_model=APIResponse[ProfessorSearchResponse])
async def search_professors(
    research_area: str = Query("", description="Research area or topic"),
    institution: str = Query("", description="University or institute name"),
    country: str = Query("", description="Country"),
    region: str = Query("", description="Region or state"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=25),
    db: Session = Depends(get_db),
    scraper: UniversityProfileScraper = Depends(get_scraper_service),
) -> APIResponse[ProfessorSearchResponse]:
    try:
        terms = [research_area, institution, country, region, "professor faculty research email"]
        query = " ".join(term.strip() for term in terms if term and term.strip())
        if not query:
            query = "computer science professor faculty research email"

        professors = await _search_openalex(
            research_area=research_area,
            institution=institution,
            country=country,
            region=region,
            page=page,
            limit=limit,
        )

        if len(professors) < limit:
            hits = await _search_web(query=query, limit=max(limit, 6))
            for hit in hits:
                if len(professors) >= limit:
                    break
                try:
                    professor = await scraper.scrape(hit["url"])
                except Exception:
                    professor = None

                if professor and (professor.name != "Unknown Name" or professor.email):
                    biography = professor.biography or hit["snippet"]
                    professors.append(
                        ProfessorSearchResult(
                            name=professor.name,
                            university=professor.university,
                            department=professor.department,
                            email=str(professor.email) if professor.email else None,
                            website=str(professor.website) if professor.website else hit["url"],
                            country=country or None,
                            research_interests=_extract_interests(biography, research_area),
                            recent_publications=[],
                            recent_work=_extract_recent_work(biography),
                            biography=biography[:1200],
                        )
                    )

        deduped = _dedupe_professors(professors)[:limit]
        for result in deduped:
            _upsert_professor(db, result)
        db.commit()

        user = get_or_create_default_user(db)
        record_search(
            db,
            user.id,
            query=query,
            research_area=research_area,
            institution=institution,
            country=country,
            region=region,
            results_count=len(deduped),
        )
        log_activity(
            db,
            user.id,
            event_type="search",
            entity_type="discovery",
            details={
                "query": query,
                "research_area": research_area,
                "institution": institution,
                "country": country,
                "region": region,
                "page": page,
                "count": len(deduped),
            },
        )
        data = ProfessorSearchResponse(query=query, count=len(deduped), page=page, limit=limit, professors=deduped)
        return APIResponse(success=True, data=data, message=f"{DISCOVERY_ENGINE_VERSION}: found {len(deduped)} professor profiles")
    except Exception as exc:
        db.rollback()
        data = ProfessorSearchResponse(query=research_area or institution or "search", count=0, page=page, limit=limit, professors=[])
        return APIResponse(success=True, data=data, message=f"{DISCOVERY_ENGINE_VERSION}: search could not complete: {type(exc).__name__}: {exc}")


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
    region: str,
    page: int,
    limit: int,
) -> list[ProfessorSearchResult]:
    if limit <= 0:
        return []

    settings = get_settings()
    headers = {"User-Agent": f"research-mail/1.0 (mailto:{settings.OPENALEX_MAILTO})"}
    institution_id: str | None = None
    institution_name = institution
    country_code = _country_to_code(country)
    works_results: list[dict] = []
    async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers=headers) as client:
        if institution:
            inst_response = await client.get(
                "https://api.openalex.org/institutions",
                params={"search": institution, "per-page": 5},
            )
            if inst_response.status_code == 200:
                inst_results = inst_response.json().get("results", [])
                inst_match = _pick_institution(inst_results, institution, country_code)
                if inst_match:
                    raw_institution_id = inst_match.get("id")
                    institution_id = raw_institution_id.rsplit("/", 1)[-1] if raw_institution_id else None
                    institution_name = inst_match.get("display_name") or institution

        works_query = research_area or institution or region or "research"
        works_response = await client.get(
            "https://api.openalex.org/works",
            params={
                "search": works_query,
                "per-page": max(limit * 8, 24),
                "page": page,
                "sort": "publication_date:desc",
            },
        )
        if works_response.status_code == 200:
            works_results = works_response.json().get("results", [])

        authors_results: list[dict] = []
        authors_response = await client.get(
            "https://api.openalex.org/authors",
            params={
                "search": " ".join(part for part in [research_area, institution, region] if part).strip() or works_query,
                "per-page": max(limit * 4, 12),
                "page": page,
            },
        )
        if authors_response.status_code == 200:
            authors_results = authors_response.json().get("results", [])

        combined = _professors_from_openalex_works(
            works_results,
            institution_id=institution_id,
            institution_name=institution_name,
            institution_filter=institution,
            country_filter=country,
            research_area=research_area,
            limit=limit,
        )
        combined.extend(
            _professors_from_openalex_authors(
                authors_results,
                institution_filter=institution,
                country_filter=country,
                research_area=research_area,
                limit=limit,
            )
        )
        return _dedupe_professors(combined)[:limit]


def _professors_from_openalex_works(
    works: list[dict],
    institution_id: str | None,
    institution_name: str,
    institution_filter: str,
    country_filter: str,
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
            resolved_country = institution.get("country_code") or institution.get("country")
            if institution_filter and institution_filter.lower() not in resolved_institution.lower():
                continue
            if country_filter and resolved_country and not _country_matches(country_filter, resolved_country):
                continue
            raw_affiliations = " ".join(authorship.get("raw_affiliation_strings") or [])
            email = _extract_email(raw_affiliations)

            record = by_author.setdefault(author_id, {
                "name": author_name,
                "university": resolved_institution,
                "country": _normalize_country(resolved_country),
                "email": email,
                "website": author.get("id"),
                "topics": [],
                "works": [],
            })
            if email and not record["email"]:
                record["email"] = email
            record["topics"].extend(topics)
            record["works"].append(f"{title} ({work.get('publication_year', 'n.d.')})")

            if len(by_author) >= limit * 3:
                break
        if len(by_author) >= limit * 3:
            break

    results: list[ProfessorSearchResult] = []
    for record in by_author.values():
        topics = list(dict.fromkeys(item for item in record["topics"] if item))[:6]
        publications = list(dict.fromkeys(record["works"]))[:5]
        works_text = "; ".join(publications[:3])
        results.append(
            ProfessorSearchResult(
                name=record["name"],
                university=record["university"],
                email=record["email"],
                website=record["website"],
                country=record["country"],
                research_interests=topics,
                recent_publications=publications,
                recent_work=works_text,
                biography=works_text,
            )
        )
        if len(results) >= limit:
            break
    return results


def _professors_from_openalex_authors(
    authors: list[dict],
    institution_filter: str,
    country_filter: str,
    research_area: str,
    limit: int,
) -> list[ProfessorSearchResult]:
    results: list[ProfessorSearchResult] = []
    for author in authors:
        name = author.get("display_name")
        institution = (author.get("last_known_institution") or {}).get("display_name") or "Unknown Institution"
        country = (author.get("last_known_institution") or {}).get("country_code")
        if not name or _looks_like_group_author(name):
            continue
        if institution_filter and institution_filter.lower() not in institution.lower():
            continue
        if country_filter and country and not _country_matches(country_filter, country):
            continue
        concepts = [
            concept.get("display_name")
            for concept in (author.get("x_concepts") or [])[:6]
            if concept.get("display_name")
        ]
        if research_area:
            concepts.insert(0, research_area.title())
        results.append(
            ProfessorSearchResult(
                name=name,
                university=institution,
                country=_normalize_country(country),
                website=author.get("id"),
                research_interests=list(dict.fromkeys(concepts))[:6],
                recent_publications=[],
                recent_work=f"{author.get('works_count', 0)} indexed works on OpenAlex",
                biography=f"{name} has {author.get('works_count', 0)} indexed works and {author.get('cited_by_count', 0)} citations.",
            )
        )
        if len(results) >= limit:
            break
    return results


def _looks_like_group_author(name: str) -> bool:
    lowered = name.lower()
    return any(word in lowered for word in ["consortium", "collaboration", "group", "committee", "society"])


def _extract_email(text: str) -> str | None:
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0).lower() if match else None


def _openalex_institution_ids(institution: dict) -> list[str]:
    values = [institution.get("id") or "", *(institution.get("lineage") or [])]
    return [value.rsplit("/", 1)[-1] for value in values if value]


def _extract_interests(text: str, seed: str) -> list[str]:
    candidates = [
        "artificial intelligence", "machine learning", "deep learning", "computer vision",
        "natural language processing", "robotics", "data science", "bioinformatics",
        "systems", "security", "networks", "human-computer interaction", "databases",
        "algorithms", "theory", "software engineering", "health", "climate", "energy",
        "synthetic biology", "biotechnology",
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
    if not existing:
        existing = db.query(ProfessorDB).filter(
            ProfessorDB.name == professor.name,
            ProfessorDB.university == professor.university,
        ).first()

    if existing:
        existing.name = professor.name
        existing.university = professor.university
        existing.department = professor.department
        existing.website = professor.website
        existing.country = professor.country
        existing.research_interests = professor.research_interests
        existing.recent_publications = professor.recent_publications
        existing.biography = professor.biography
        existing.source = "discovery"
        existing.last_scraped_at = datetime.utcnow()
        _upsert_profile_and_publications(db, existing, professor)
        return

    db_professor = ProfessorDB(
        name=professor.name,
        university=professor.university,
        department=professor.department,
        email=professor.email,
        website=professor.website,
        country=professor.country,
        research_interests=professor.research_interests,
        recent_publications=professor.recent_publications,
        biography=professor.biography,
        source="discovery",
        source_metadata={"recent_work": professor.recent_work},
        last_scraped_at=datetime.utcnow(),
    )
    db.add(db_professor)
    db.flush()
    _upsert_profile_and_publications(db, db_professor, professor)


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


def _upsert_profile_and_publications(db: Session, db_professor: ProfessorDB, professor: ProfessorSearchResult) -> None:
    profile = db.query(ResearchProfileDB).filter(ResearchProfileDB.professor_id == db_professor.id).first()
    if not profile:
        profile = ResearchProfileDB(professor_id=db_professor.id)
        db.add(profile)
    profile.summary = professor.recent_work or professor.biography
    profile.website_content = professor.biography
    profile.institution = professor.university
    profile.country = professor.country
    profile.research_interests = professor.research_interests
    profile.recent_publications = professor.recent_publications

    for publication_title in professor.recent_publications[:5]:
        exists = db.query(PublicationDB).filter(
            PublicationDB.professor_id == db_professor.id,
            PublicationDB.title == publication_title,
        ).first()
        if exists:
            continue
        db.add(PublicationDB(professor_id=db_professor.id, title=publication_title, source="openalex"))


def _save_scraped_professor(db: Session, professor: Professor, source_url: str) -> Professor:
    result = ProfessorSearchResult(
        name=professor.name,
        university=professor.university,
        department=professor.department,
        email=str(professor.email) if professor.email else None,
        website=str(professor.website) if professor.website else source_url,
        country=professor.country,
        research_interests=professor.research_interests,
        recent_publications=professor.recent_publications,
        recent_work=_extract_recent_work(professor.biography or ""),
        biography=professor.biography or "",
    )
    _upsert_professor(db, result)
    db.commit()
    stored = db.query(ProfessorDB).filter(ProfessorDB.website == result.website).first()
    if not stored and result.email:
        stored = db.query(ProfessorDB).filter(ProfessorDB.email == result.email).first()
    return Professor.model_validate(stored)


def _dedupe_professors(professors: list[ProfessorSearchResult]) -> list[ProfessorSearchResult]:
    unique: dict[str, ProfessorSearchResult] = {}
    for professor in professors:
        key = professor.email or professor.website or f"{professor.name}|{professor.university}"
        if key not in unique:
            unique[key] = professor
    return list(unique.values())


def _pick_institution(institutions: list[dict], institution_filter: str, country_code: str | None) -> dict | None:
    for institution in institutions:
        name = (institution.get("display_name") or "").lower()
        if institution_filter.lower() in name:
            if not country_code or institution.get("country_code") == country_code:
                return institution
    return institutions[0] if institutions else None


def _country_to_code(country: str) -> str | None:
    mapping = {
        "usa": "US",
        "united states": "US",
        "united kingdom": "GB",
        "uk": "GB",
        "india": "IN",
        "canada": "CA",
        "germany": "DE",
        "france": "FR",
        "china": "CN",
        "japan": "JP",
        "singapore": "SG",
        "australia": "AU",
    }
    normalized = country.strip().lower()
    if not normalized:
        return None
    if len(country.strip()) == 2:
        return country.strip().upper()
    return mapping.get(normalized)


def _country_matches(expected: str, actual: str) -> bool:
    expected_code = _country_to_code(expected) or expected.strip().upper()
    actual_code = actual.strip().upper()
    return expected_code == actual_code or expected.strip().lower() == (_normalize_country(actual) or "").lower()


def _normalize_country(value: str | None) -> str | None:
    if not value:
        return None
    mapping = {
        "US": "United States",
        "GB": "United Kingdom",
        "IN": "India",
        "CA": "Canada",
        "DE": "Germany",
        "FR": "France",
        "CN": "China",
        "JP": "Japan",
        "SG": "Singapore",
        "AU": "Australia",
    }
    cleaned = value.strip().upper()
    return mapping.get(cleaned, value)
