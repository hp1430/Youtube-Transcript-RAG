from functools import lru_cache
from langchain_openai import OpenAIEmbeddings

from app.configs.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

@lru_cache
def get_embeddings() -> OpenAIEmbeddings:
    """Get the embeddings for the application."""
    settings = get_settings()
    logger.info(f"Initializing OpenAI embeddings with model: {settings.embedding_model}")
    return OpenAIEmbeddings(
        model = settings.embedding_model,
        openai_api_type = settings.openai_api_key
    )