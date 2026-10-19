from doctest import UnexpectedException
from functools import lru_cache
import uuid
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

from app.configs.settings import get_settings
from app.services.embedding_service import get_embeddings
from app.utils.logger import get_logger

logger = get_logger(__name__)

EMBEDDING_DIMENSIONS = 1536

@lru_cache
def get_qdrant_client() -> QdrantClient:
    """Get the Qdrant client for the application."""
    settings = get_settings()
    logger.info(f"Initializing Qdrant client with URL: {settings.qdrant_url}")
    return QdrantClient(
        url = settings.qdrant_url,
    )

class VectorStoreRepository:

    def __init__(self, collection_name: str | None = None):
        settings = get_settings()

        self.collection_name = collection_name or settings.collection_name
        self.client = get_qdrant_client()
        self._vector_store: QdrantVectorStore | None = None

        logger.info(f"Initialized VectorStoreRepository for collection: {self.collection_name}")

    @property
    def vector_store(self) -> QdrantVectorStore:
        if self._vector_store is None:
            self._vector_store = QdrantVectorStore(
                client=self.client,
                collection_name=self.collection_name,
                embedding=get_embeddings()
            )

        return self._vector_store

    def _ensure_collection(self) -> None:
        try:
            _info = self.client.get_collection(self.collection_name)
        except UnexpectedException:
            logger.info(f"Collection {self.collection_name} not found. Creating...")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=get_embeddings().dimensions or EMBEDDING_DIMENSIONS,
                    distance=Distance.COSINE,
                )
            )

    def add_documents(self, documents: list[Document]) -> list[str]:
        if not documents:
            return []

        ids = [str(uuid.uuid4()) for _ in documents]
        self.vector_store.add_documents(documents, ids = ids)
        logger.info(f"Added {len(documents)} documents to collection {self.collection_name}")
        return ids

    def delete_collection(self) -> None:
        self.client.delete_collection(self.collection_name)

    def search_with_score(self, query: str, k: int | None = None) -> list[tuple[Document, float]]:
        settings = get_settings()
        k = k or settings.retrieval_k
        return self.vector_store.similarity_search_with_score(query, k=k)

    def search(self, query: str, k: int | None = None) -> list[Document]:
        settings = get_settings()
        k = k or settings.retrieval_k
        return self.vector_store.similarity_search(query, k=k)

    def health_check(self) -> bool:
        try:
            self.client.get_collection(self.collection_name)
            logger.info(f"Health check passed for collection {self.collection_name}")
            return True
        except Exception as e:
            print(f"Health check failed: {e}")
            return False