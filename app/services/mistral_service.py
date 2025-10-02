import asyncio
import time
from typing import List, Optional
from contextlib import asynccontextmanager
import threading
from concurrent.futures import ThreadPoolExecutor

from mistral_common.protocol.instruct.tool_calls import Function, Tool
from mistral_inference.transformer import Transformer
from mistral_inference.generate import generate
from mistral_common.tokens.tokenizers.mistral import MistralTokenizer
from mistral_common.protocol.instruct.messages import UserMessage, AssistantMessage, SystemMessage
from mistral_common.protocol.instruct.request import ChatCompletionRequest as MistralCompletionRequest

from app.models.schemas import ChatMessage, Role
from app.core.exceptions import (
    ModelNotLoadedException, 
    ModelLoadException, 
    TokenizationException,
    GenerationException
)
from app.utils.logging import logger
from app.config.settings import settings

class MistralService:
    """Production-grade Mistral model service with thread safety"""
    
    def __init__(self):
        self.model_path = settings.MODEL_PATH
        self.model = None
        self.tokenizer = None
        self.loaded = False
        self.loading = False
        self._lock = threading.Lock()
        self._thread_pool = ThreadPoolExecutor(max_workers=1)
        self._load_time = None
    
    def load_model(self):
        """Load model and tokenizer in a thread-safe manner"""
        with self._lock:
            if self.loaded or self.loading:
                return
            
            self.loading = True
            
            try:
                logger.info("Starting model loading", model_path=self.model_path)
                start_time = time.time()
                
                # Load tokenizer
                tokenizer_paths = [
                    f"{self.model_path}/tokenizer.model.v3",
                    f"{self.model_path}/tokenizer.model",
                    "./tokenizer.model.v3",
                    "./tokenizer.model"
                ]
                
                tokenizer_loaded = False
                for tokenizer_path in tokenizer_paths:
                    try:
                        self.tokenizer = MistralTokenizer.from_file(tokenizer_path)
                        tokenizer_loaded = True
                        logger.info("Tokenizer loaded successfully", path=tokenizer_path)
                        break
                    except Exception as e:
                        logger.warning("Failed to load tokenizer", path=tokenizer_path, error=str(e))
                        continue
                
                if not tokenizer_loaded:
                    raise ModelLoadException("Could not load tokenizer from any known path")
                
                # Load model
                self.model = Transformer.from_folder(self.model_path)
                
                self.loaded = True
                self._load_time = time.time() - start_time
                
                logger.info(
                    "Model loaded successfully", 
                    model_path=self.model_path,
                    load_time_seconds=round(self._load_time, 2)
                )
                
            except Exception as e:
                self.loaded = False
                self.loading = False
                logger.error("Model loading failed", error=str(e))
                raise ModelLoadException(f"Model loading failed: {str(e)}")
            finally:
                self.loading = False
    
    async def load_model_async(self):
        """Load model asynchronously"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self._thread_pool, self.load_model)
    
    def _convert_messages(self, messages: List[ChatMessage]) -> list:
        """Convert OpenAI format messages to Mistral format"""
        mistral_messages = []
        
        for msg in messages:
            if msg.role == Role.SYSTEM:
                mistral_messages.append(SystemMessage(content=msg.content))
            elif msg.role == Role.USER:
                mistral_messages.append(UserMessage(content=msg.content))
            elif msg.role == Role.ASSISTANT:
                mistral_messages.append(AssistantMessage(content=msg.content))
        
        return mistral_messages
    
    def _count_tokens_approximate(self, text: str) -> int:
        """Approximate token count (for monitoring)"""
        return len(text.split())  # Simple approximation
    
    def generate_completion(
        self, 
        messages: List[ChatMessage],
        max_tokens: int,
        temperature: float,
        stream: bool = False
    ) -> str:
        """Generate completion (thread-safe)"""
        if not self.loaded:
            raise ModelNotLoadedException()
        
        try:
            # Convert messages
            mistral_messages = self._convert_messages(messages)
            
            # Create completion request
            completion_request = MistralCompletionRequest(messages=mistral_messages)
            
            # Encode tokens
            tokens = self.tokenizer.encode_chat_completion(completion_request).tokens
            
            # Generate
            out_tokens, _ = generate(
                [tokens], 
                self.model, 
                max_tokens=max_tokens, 
                temperature=temperature,
                eos_id=self.tokenizer.instruct_tokenizer.tokenizer.eos_id
            )
            
            # Decode result
            result = self.tokenizer.instruct_tokenizer.tokenizer.decode(out_tokens[0])
            
            return result
            
        except Exception as e:
            logger.error("Generation failed", error=str(e))
            raise GenerationException(f"Generation failed: {str(e)}")
    
    async def generate_completion_async(
        self, 
        messages: List[ChatMessage],
        max_tokens: int,
        temperature: float,
        stream: bool = False
    ) -> str:
        """Generate completion asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._thread_pool, 
            self.generate_completion, 
            messages, max_tokens, temperature, stream
        )
    
    def get_health_status(self) -> dict:
        """Get service health status"""
        return {
            "loaded": self.loaded,
            "loading": self.loading,
            "load_time": self._load_time,
            "model_path": self.model_path
        }
    
    def shutdown(self):
        """Cleanup resources"""
        self._thread_pool.shutdown(wait=True)

# Global service instance
mistral_service = MistralService()