from fastapi import APIRouter
from .crawler_router import router as crawler_router

router = APIRouter()
router.include_router(crawler_router, prefix="/crawler")

__all__ = ['router']