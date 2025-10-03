from pydantic import BaseModel
from typing import Optional, Dict, Any

class StreamRequest(BaseModel):
    data_source: str
    chunk_size: int = 1024
    filters: Optional[Dict[str, Any]] = None
    stream_type: str = "continuous"

class StreamResponse(BaseModel):
    chunk_id: int
    data: Dict[str, Any]
    timestamp: str
    is_final: bool = False