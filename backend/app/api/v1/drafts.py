from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from uuid import UUID
from app.models.draft import Draft, DraftStatus
from app.models.response import APIResponse
from app.api.deps import get_draft_repo
from app.repository.draft_repository import DraftRepository

router = APIRouter()

@router.post("/", response_model=APIResponse[Draft])
async def create_draft(
    draft: Draft,
    repo: DraftRepository = Depends(get_draft_repo)
) -> APIResponse[Draft]:
    """Create a new email draft."""
    new_draft = await repo.create(draft)
    return APIResponse(success=True, data=new_draft, message="Draft created successfully")

@router.get("/", response_model=APIResponse[List[Draft]])
async def list_drafts(
    query: str | None = None,
    repo: DraftRepository = Depends(get_draft_repo)
) -> APIResponse[List[Draft]]:
    """List all drafts, optionally filtered by search query."""
    if query:
        drafts = await repo.search(query)
    else:
        drafts = await repo.list_all()
    return APIResponse(success=True, data=drafts)

@router.get("/{draft_id}", response_model=APIResponse[Draft])
async def get_draft(
    draft_id: UUID,
    repo: DraftRepository = Depends(get_draft_repo)
) -> APIResponse[Draft]:
    """Get a specific draft by ID."""
    draft = await repo.get_by_id(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return APIResponse(success=True, data=draft)

@router.put("/{draft_id}", response_model=APIResponse[Draft])
async def update_draft(
    draft_id: UUID,
    draft: Draft,
    repo: DraftRepository = Depends(get_draft_repo)
) -> APIResponse[Draft]:
    """Update an existing draft."""
    try:
        updated = await repo.update(draft_id, draft)
        return APIResponse(success=True, data=updated, message="Draft updated successfully")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{draft_id}", response_model=APIResponse[bool])
async def delete_draft(
    draft_id: UUID,
    repo: DraftRepository = Depends(get_draft_repo)
) -> APIResponse[bool]:
    """Delete a draft."""
    success = await repo.delete(draft_id)
    if not success:
        raise HTTPException(status_code=404, detail="Draft not found")
    return APIResponse(success=True, data=True, message="Draft deleted successfully")
