from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
import json
from typing import AsyncGenerator, List, Optional
import asyncio

from app.services.mistral_service import MistralService
from app.core.dependencies import get_mistral_service

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False

class ChatResponseChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = None

class ChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatResponseChoice]

class StreamResponseChoice(BaseModel):
    index: int
    delta: dict
    finish_reason: Optional[str] = None

class StreamResponse(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[StreamResponseChoice]

@router.post("/chat/completions")
async def chat_completions(
    request: ChatRequest,
    mistral_service: MistralService = Depends(get_mistral_service)
):
    """Chat completions endpoint with streaming support"""
    
    if request.stream:
        return await stream_chat_completions(request, mistral_service)
    else:
        return await non_stream_chat_completions(request, mistral_service)

async def stream_chat_completions(request: ChatRequest, mistral_service: MistralService):
    """Stream chat completions"""
    
    async def generate() -> AsyncGenerator[str, None]:
        try:
            # Generate a unique ID for this completion
            import time
            completion_id = f"chatcmpl-{int(time.time())}"
            
            # Start streaming
            async for token in mistral_service.stream_chat(
                messages=request.messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            ):
                # Create streaming response
                stream_response = StreamResponse(
                    id=completion_id,
                    created=int(time.time()),
                    model="mistral",
                    choices=[
                        StreamResponseChoice(
                            index=0,
                            delta={"content": token}
                        )
                    ]
                )
                yield f"data: {stream_response.json()}\n\n"
            
            # Send final chunk with finish reason
            final_response = StreamResponse(
                id=completion_id,
                created=int(time.time()),
                model="mistral",
                choices=[
                    StreamResponseChoice(
                        index=0,
                        delta={},
                        finish_reason="stop"
                    )
                ]
            )
            yield f"data: {final_response.json()}\n\n"
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            error_response = {
                "error": {
                    "message": str(e),
                    "type": "api_error"
                }
            }
            yield f"data: {json.dumps(error_response)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        }
    )

async def non_stream_chat_completions(request: ChatRequest, mistral_service: MistralService):
    """Non-streaming chat completions"""
    try:
        import time
        completion_id = f"chatcmpl-{int(time.time())}"
        
        # Get complete response
        full_response = await mistral_service.chat(
            messages=request.messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        response = ChatResponse(
            id=completion_id,
            created=int(time.time()),
            model="mistral",
            choices=[
                ChatResponseChoice(
                    index=0,
                    message=ChatMessage(
                        role="assistant",
                        content=full_response
                    ),
                    finish_reason="stop"
                )
            ]
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stream/health")
async def stream_health():
    return {"status": "healthy", "streaming": True}

@router.options("/chat/completions")
async def options_chat_completions():
    """Handle OPTIONS request for CORS"""
    return {"status": "ok"}