import asyncio
import json
import time
from typing import AsyncGenerator
from app.models.streaming_models import StreamRequest, StreamResponse

class StreamingService:
    async def stream_data(self, request: StreamRequest) -> AsyncGenerator[StreamResponse, None]:
        """Stream data chunks asynchronously"""
        chunk_id = 0
        
        # Simulate data streaming - replace with your actual data source
        while True:
            chunk_data = {
                "message": f"Chunk {chunk_id}",
                "source": request.data_source,
                "size": request.chunk_size
            }
            
            yield StreamResponse(
                chunk_id=chunk_id,
                data=chunk_data,
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                is_final=False
            )
            
            chunk_id += 1
            await asyncio.sleep(0.1)  # Control stream rate
            
            # Break condition - replace with your actual logic
            if chunk_id >= 100:  # Limit for demo
                break
        
        # Final chunk
        yield StreamResponse(
            chunk_id=chunk_id,
            data={"message": "Stream complete"},
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            is_final=True
        )