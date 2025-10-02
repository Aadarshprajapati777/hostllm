from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
import time
import uuid
import json

from app.models.schemas import (
    ChatCompletionRequest, ChatCompletionResponse, ChatCompletionChoice,
    UsageStats, ModelsListResponse, ModelInfo, ChatMessage, Role
)
from app.api.dependencies import APIKeyDep, MistralServiceDep
from app.utils.logging import logger
from app.config.settings import settings

router = APIRouter()

@router.post(
    "/chat/completions",
    response_model=ChatCompletionResponse,
    status_code=status.HTTP_200_OK,
    summary="Create chat completion",
    description="Generate a chat completion using the Mistral model"
)
async def create_chat_completion(
    request: ChatCompletionRequest,
    api_key: APIKeyDep,
    mistral_service: MistralServiceDep
):
    """Create chat completion"""
    try:
        start_time = time.time()
        
        logger.info(
            "Chat completion request",
            model=request.model,
            message_count=len(request.messages),
            max_tokens=request.max_tokens,
            stream=request.stream
        )
        
        if request.stream:
            return await handle_streaming_completion(request, mistral_service)
        else:
            return await handle_normal_completion(request, mistral_service, start_time)
            
    except Exception as e:
        logger.error("Chat completion failed", error=str(e))
        raise

async def handle_normal_completion(
    request: ChatCompletionRequest,
    mistral_service: MistralServiceDep,
    start_time: float
) -> ChatCompletionResponse:
    """Handle non-streaming completion"""
    # Generate completion
    response_text = await mistral_service.generate_completion_async(
        messages=request.messages,
        max_tokens=request.max_tokens or settings.MAX_TOKENS,
        temperature=request.temperature or settings.DEFAULT_TEMPERATURE,
        stream=False
    )
    
    # Calculate tokens (approximate)
    prompt_tokens = sum(
        mistral_service._count_tokens_approximate(msg.content) 
        for msg in request.messages
    )
    completion_tokens = mistral_service._count_tokens_approximate(response_text)
    
    # Log performance
    processing_time = time.time() - start_time
    logger.info(
        "Chat completion completed",
        processing_time=round(processing_time, 2),
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens
    )
    
    # Create response
    return ChatCompletionResponse(
        id=f"chatcmpl-{uuid.uuid4()}",
        created=int(start_time),
        model=request.model,
        choices=[
            ChatCompletionChoice(
                index=0,
                message=ChatMessage(role=Role.ASSISTANT, content=response_text),
                finish_reason="stop"
            )
        ],
        usage=UsageStats(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens
        )
    )

async def handle_streaming_completion(
    request: ChatCompletionRequest,
    mistral_service: MistralServiceDep
) -> StreamingResponse:
    """Handle streaming completion"""
    async def generate_stream():
        try:
            response_text = await mistral_service.generate_completion_async(
                messages=request.messages,
                max_tokens=request.max_tokens or settings.MAX_TOKENS,
                temperature=request.temperature or settings.DEFAULT_TEMPERATURE,
                stream=False
            )
            
            # Send response as a single chunk (simplified streaming)
            chunk = {
                "id": f"chatcmpl-{uuid.uuid4()}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": request.model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {"role": "assistant", "content": response_text},
                        "finish_reason": "stop"
                    }
                ]
            }
            
            yield f"data: {json.dumps(chunk)}\n\n"
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            error_chunk = {
                "error": {
                    "message": str(e),
                    "type": "internal_error",
                    "code": "generation_failed"
                }
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable buffering for nginx
        }
    )

@router.get(
    "/models",
    response_model=ModelsListResponse,
    summary="List models",
    description="List available models"
)
async def list_models(api_key: APIKeyDep):
    """List available models"""
    models = [
        ModelInfo(
            id=settings.MODEL_PATH,
            created=int(time.time()),
            owned_by="mistral"
        )
    ]
    return ModelsListResponse(data=models)