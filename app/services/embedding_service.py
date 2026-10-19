from functools import lru_cache
from docx import settings
from langchain_openai import OpenAIEmbeddings

from app.configs.settings import get_settings


@lru_cache
def get_embeddings() -> OpenAIEmbeddings:
    """Get the embeddings for the application."""
    settings = get_settings()
    return OpenAIEmbeddings(
        model = settings.embedding_model,
        openai_api_type = settings.openai_api_key
    )