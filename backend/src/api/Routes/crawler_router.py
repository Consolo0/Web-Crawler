from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio

from src.api.Controllers.Controller import Controller
from src.Db.Db import Db

router = APIRouter()

class CrawlerRequest(BaseModel):
    query: str
    restrictions: Optional[Dict[str, Any]] = {}

db = Db()

@router.post("/")
async def crawl(request: CrawlerRequest):
    """Run crawler and return all results at once."""
    controller = Controller(request.query, db)
    result = await asyncio.to_thread(controller.run, request.restrictions)
    
    return {
        "status": "completed",
        "query": request.query,
        "results": result
    }

@router.post("/stream")
async def crawl_stream(request: CrawlerRequest):
    """Stream crawler results in real-time using Server-Sent Events."""
    return {"status": "On Work"}