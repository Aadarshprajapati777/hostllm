from fastapi import HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
import time
from collections import defaultdict
import asyncio

from .settings import settings

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests = defaultdict(list)
    
    async def is_rate_limited(self, key: str, limit: int, window: int = 60) -> bool:
        """Check if request is rate limited"""
        now = time.time()
        self.requests[key] = [req_time for req_time in self.requests[key] if now - req_time < window]
        
        if len(self.requests[key]) >= limit:
            return True
        
        self.requests[key].append(now)
        return False

rate_limiter = RateLimiter()

class APIKeyBearer(HTTPBearer):
    """API Key authentication scheme"""
    
    async def __call__(self, request: Request) -> str:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        
        if credentials.scheme != "Bearer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authentication scheme"
            )
        
        if credentials.credentials not in settings.API_KEYS:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        
        # Rate limiting by API key
        if await rate_limiter.is_rate_limited(
            f"api_key_{credentials.credentials}", 
            settings.RATE_LIMIT_PER_MINUTE
        ):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        return credentials.credentials

security = APIKeyBearer()