import asyncio
from typing import AsyncGenerator, Any

class StreamManager:
    def __init__(self):
        self.active_streams = {}
    
    async def create_stream(self, stream_id: str, data_source: str):
        """Create a new stream"""
        self.active_streams[stream_id] = {
            "data_source": data_source,
            "active": True
        }
    
    def stop_stream(self, stream_id: str):
        """Stop a specific stream"""
        if stream_id in self.active_streams:
            self.active_streams[stream_id]["active"] = False

stream_manager = StreamManager()
