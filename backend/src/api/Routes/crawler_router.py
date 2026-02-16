from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import json
import threading
from queue import Queue
from src.api.Controllers.Controller import Controller
from src.api.Controllers.StreamingController import StreamingController
from src.Db.Db import Db
from src.Helpers.Serializer import Serializer

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
    """
    Stream crawler results in real-time using Server-Sent Events.
    
    Events sent:
    - status: Crawl progress updates
    - listing_result: Product listings from a page
    - error: Errors encountered
    - done: Crawl complete with summary
    """
    
    async def event_generator():
        """
        Generator that yields Server-Sent Events.
        Runs the crawler in a thread and streams results.
        """
        # Create streaming controller
        controller = StreamingController(request.query, db)
        
        # Queue to bridge sync generator to async
        result_queue = Queue()
        done_event = threading.Event()
        
        def run_crawler():
            """Run crawler in background thread and put results in queue."""
            try:
                for event in controller.run(request.restrictions):
                    result_queue.put(("event", event))
            except Exception as e:
                import traceback
                traceback.print_exc()
                result_queue.put(("event", {
                    "type": "error",
                    "message": "Crawler error",
                    "error": str(e)
                }))
            finally:
                done_event.set()
        
        # Start crawler in background thread
        crawler_thread = threading.Thread(target=run_crawler, daemon=True)
        crawler_thread.start()
        
        try:
            # Yield events as they come from the queue
            while not done_event.is_set() or not result_queue.empty():
                if not result_queue.empty():
                    msg_type, event = result_queue.get()
                    
                    try:
                        # Serialize event data
                        serialized_event = Serializer.serialize_event(event=event)
                        
                        # Format as Server-Sent Event
                        event_type = serialized_event.get("type", "message")
                        yield f"event: {event_type}\n"
                        yield f"data: {json.dumps(serialized_event)}\n\n"
                    
                    except Exception as e:
                        # If serialization fails, send error event
                        import traceback
                        traceback.print_exc()
                        yield f"event: error\n"
                        yield f"data: {json.dumps({'type': 'error', 'message': 'Serialization error', 'error': str(e)})}\n\n"
                else:
                    # Small delay to prevent busy waiting
                    await asyncio.sleep(0.1)
            
            # Wait for thread to complete
            crawler_thread.join(timeout=5)
            
        except Exception as e:
            # Send error event
            import traceback
            traceback.print_exc()
            yield f"event: error\n"
            yield f"data: {json.dumps({'type': 'error', 'message': 'Stream error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
            "Connection": "keep-alive",
        }
    )