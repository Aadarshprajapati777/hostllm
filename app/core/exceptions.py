from fastapi import HTTPException, status
from typing import Any, Dict

class MistralAPIException(HTTPException):
    """Base exception for Mistral API errors"""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str = None,
        error_type: str = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.error_type = error_type

class ModelNotLoadedException(MistralAPIException):
    def __init__(self, detail: str = "Model is not loaded"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code="model_not_loaded",
            error_type="service_unavailable"
        )

class ModelLoadException(MistralAPIException):
    def __init__(self, detail: str = "Failed to load model"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="model_load_failed",
            error_type="internal_error"
        )

class TokenizationException(MistralAPIException):
    def __init__(self, detail: str = "Tokenization failed"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="tokenization_failed",
            error_type="invalid_request"
        )

class GenerationException(MistralAPIException):
    def __init__(self, detail: str = "Generation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="generation_failed",
            error_type="internal_error"
        )