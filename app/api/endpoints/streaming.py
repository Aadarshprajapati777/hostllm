from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
import json
from typing import AsyncGenerator

from app.services.streaming_service import StreamingService
from app.models.streaming_models import StreamRequest, StreamResponse

router = APIRouter()

@router.post("/stream")
async def stream_data(request: StreamRequest):
    """Stream data in real-time"""
    streaming_service = StreamingService()
    
    async def generate() -> AsyncGenerator[str, None]:
        async for chunk in streaming_service.stream_data(request):
            yield f"data: {json.dumps(chunk.dict())}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

@router.get("/stream/health")
async def stream_health():
    return {"status": "healthy", "streaming": True}