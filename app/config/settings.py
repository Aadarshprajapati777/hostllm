import os
from typing import List

class Settings:
    """Simplified application settings without complex parsing"""
    
    def __init__(self):
        # Server
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", "8000"))
        self.WORKERS = int(os.getenv("WORKERS", "1"))
        self.RELOAD = os.getenv("RELOAD", "false").lower() == "true"
        
        # Model
        self.MODEL_PATH = os.getenv("MODEL_PATH", "Aadarsh183/Mentay-Files")
        self.MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))
        self.DEFAULT_TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
        self.DEFAULT_TOP_P = float(os.getenv("TOP_P", "1.0"))
        
        # Security - Handle comma-separated lists
        api_keys_str = os.getenv("API_KEYS", "token-abc123")
        self.API_KEYS = [key.strip() for key in api_keys_str.split(",") if key.strip()]
        
        cors_origins_str = os.getenv("CORS_ORIGINS", "*")
        self.CORS_ORIGINS = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]
        
        self.RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
        
        # Monitoring
        self.ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        
        # Performance
        self.MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "100"))
        self.REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "300"))

settings = Settings()