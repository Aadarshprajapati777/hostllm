from app.services.mistral_service import MistralService

async def get_mistral_service() -> MistralService:
    # This should return your initialized MistralService instance
    # You might want to use a singleton pattern or dependency injection
    from app.main import mistral_service
    return mistral_service