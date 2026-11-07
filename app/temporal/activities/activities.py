from pathlib import Path

from docx import document
from langchain_core.documents import Document
from temporalio import activity, service

from app.repositories.vector_store_repository import VectorStoreRepository
from app.services.document_service import DocumentService
from app.utils import get_logger

logger = get_logger(__name__)

def _to_dicts(documents: list[Document]) -> list[dict]:
    return [
        {
            "page_content": doc.page_content,
            "metadata": doc.metadata
        } for doc in documents
    ]

def _from_dict(payload: list[dict]) -> list[Document]:
    return [Document(page_content=doc["page_content"], metadata=doc["metadata"]) for doc in payload]

@activity.defn(name="parse_documents_activity")
async def parse_documents_activity(local_path: str, filename: str) -> list[dict]:
    activity.logger.info(f"Parsing documents from {local_path} with filename {filename}")
    service = DocumentService()
    docs = service.load_file(Path(local_path), source_name=filename)
    return _to_dicts(docs)

@activity.defn(name="chunk_documents_activity")
async def chunk_documents_activity(documents: list[dict]) -> list[dict]:
    activity.logger.info(f"Chunking {len(documents)} documents")
    service = DocumentService()
    chunks = service.split_documents(_from_dict(documents))
    activity.logger.info(f"Chunked {len(chunks)} documents")
    return _to_dicts(chunks)

@activity.defn(name="index_documents_activity")
async def index_documents_activity(chunks: list[dict]) -> int:
    if not chunks:
        return 0
    repo = VectorStoreRepository()
    doc_chunks = _from_dict(chunks)
    ids = repo.add_documents(doc_chunks)
    activity.logger.info(f"Indexed {len(ids)} chunks")
    return len(ids)
