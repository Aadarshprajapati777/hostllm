from fastapi import APIRouter, status
import time

from app.models.schemas import ModelsListResponse, ModelInfo
from app.api.dependencies import APIKeyDep
from app.config.settings import settings

router = APIRouter()

@router.get(
    "",
    response_model=ModelsListResponse,
    status_code=status.HTTP_200_OK,
    summary="List models",
    description="List all available models"
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