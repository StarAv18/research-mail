from fastapi import APIRouter
from app.api.v1 import system

api_router = APIRouter()

# Aggregate all v1 routers
api_router.include_router(system.router, prefix="/system")
