from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Env settings for the application"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # OpenAI
    openai_api_key: str = ""

    # Qdrant
    qdrant_url: str = ""

    # Temporal
    temporal_host: str = ""
    temporal_namespace: str = ""
    temporal_task_queue: str = ""

    # Collection and models
    collection_name: str = ""
    embedding_model: str = ""
    llm_model: str = ""
    llm_temperature: float = 0.0
    chunk_size: int = 1000
    chunk_overlap: int = 200
    retrieval_k: int = 4

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"
    app_name: str = "YoutubeTranscriptNaiveRagDemo"

    # Upload limits
    max_files_per_upload: int = 10
    index_batch_size: int = 100

    # Ingestion mode
    use_temporal_ingestion: bool = False
    upload_dir: str = "uploads"

    # Optional RAGAS evaluation (Stage 6)
    enable_ragas_evaluation: bool = False

@lru_cache
def get_settings() -> Settings:
    """Get the settings for the application"""
    return Settings()