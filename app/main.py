from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import uuid

from app.core.events import lifespan
from app.core.exceptions import MistralAPIException
from app.api.endpoints import chat, models
from app.config.settings import settings
from app.utils.logging import logger
from app.models.schemas import HealthResponse, ServerInfo
from app.api.endpoints import streaming  # NEW

# Create FastAPI app
app = FastAPI(
    title="Mistral Production API",
    description="Production-grade OpenAI-compatible API for Mistral models",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(MistralAPIException)
async def mistral_exception_handler(request, exc: MistralAPIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "code": exc.error_code,
            "type": exc.error_type
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    logger.error("Unhandled exception", error=str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "code": "internal_error",
            "type": "internal_server_error"
        }
    )

# Include routers
app.include_router(
    chat.router,
    prefix="/v1",
    tags=["chat"]
)

app.include_router(
    models.router,
    prefix="/v1/models",
    tags=["models"]
)

# Include streaming router
app.include_router(
    streaming.router,
    prefix="/api/v1",
    tags=["streaming"]
)

# Health and info endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    from app.services.mistral_service import mistral_service
    return HealthResponse(
        status="healthy" if mistral_service.loaded else "degraded",
        model_loaded=mistral_service.loaded,
        timestamp=int(time.time())
    )

@app.get("/info", response_model=ServerInfo)
async def server_info():
    return ServerInfo(
        name="Mistral Production API",
        version="2.0.0",
        status="running",
        model=settings.MODEL_PATH,
        max_concurrent_requests=settings.MAX_CONCURRENT_REQUESTS
    )

@app.get("/")
async def root():
    return {
        "message": "Mistral Production API Server",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        reload=settings.RELOAD
    )