from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.services.mistral_service import mistral_service
from app.utils.logging import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("Starting Mistral API Server")
    
    # Load model asynchronously
    try:
        await mistral_service.load_model_async()
        logger.info("Application startup completed")
    except Exception as e:
        logger.error("Application startup failed", error=str(e))
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Mistral API Server")
    mistral_service.shutdown()
    logger.info("Application shutdown completed")