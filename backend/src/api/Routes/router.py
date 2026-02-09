from fastapi import APIRouter
from .crawler import router as crawler_router

router = APIRouter()

router.include_router(crawler_router, tags=["crawler"], prefix="/crawler")
