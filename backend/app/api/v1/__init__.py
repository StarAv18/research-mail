from fastapi import APIRouter
from app.api.v1 import system, drafts, outreach, discovery

api_router = APIRouter()

# Aggregate all v1 routers
api_router.include_router(system.router, prefix="/system", tags=["System"])
api_router.include_router(drafts.router, prefix="/drafts", tags=["Drafts"])
api_router.include_router(outreach.router, prefix="/outreach", tags=["Outreach"])
api_router.include_router(discovery.router, prefix="/discovery", tags=["Discovery"])
