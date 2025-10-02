from fastapi import Depends, HTTPException, status
from typing import Annotated

from app.config.security import security
from app.services.mistral_service import mistral_service
from app.utils.logging import logger

async def get_api_key(api_key: str = Depends(security)) -> str:
    """Dependency to get and validate API key"""
    return api_key

async def get_mistral_service():
    """Dependency to get Mistral service instance"""
    if not mistral_service.loaded and not mistral_service.loading:
        logger.warning("Model not loaded, attempting to load")
        await mistral_service.load_model_async()
    
    if not mistral_service.loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model service is not available"
        )
    
    return mistral_service

# Type annotations for dependencies
APIKeyDep = Annotated[str, Depends(get_api_key)]
MistralServiceDep = Annotated[any, Depends(get_mistral_service)]