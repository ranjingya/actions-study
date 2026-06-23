from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.home import router as home_router

api_router = APIRouter()
api_router.include_router(home_router)
api_router.include_router(health_router)
