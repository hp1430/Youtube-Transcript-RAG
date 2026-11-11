from importlib import metadata
import json
from pathlib import Path

from docx import document
from langchain_core.documents import Document
from temporalio import activity, service

from app.configs.settings import get_settings
from app.repositories.vector_store_repository import VectorStoreRepository
from app.services.document_service import DocumentService
from app.services.ingestion_service import IngestionService
from app.utils import get_logger
from app.utils.doc_chunk_writing import count_jsonl_lines, read_documents_from_jsonl_batch, spill_path_for_upload, write_documents_to_jsonl

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

@activity.defn(name="parse_documents_to_jsonl_activity")
async def parse_documents_to_jsonl_activity(local_path: str, filename: str) -> dict:
    upload_path = Path(local_path)
    write_path = spill_path_for_upload(upload_path, filename, "parsed")
    activity.logger.info(f"Parsing documents from {local_path} with filename {filename} to {write_path}")
    service = DocumentService()
    docs = service.load_file(Path(local_path), source_name=filename)
    count = write_documents_to_jsonl(write_path, docs)
    line_count = count_jsonl_lines(write_path)
    activity.logger.info(f"Parsed {count} documents from {local_path} with filename {filename} to {write_path}")
    return {
        "write_path": str(write_path),
        "line_count": line_count,
        "stage": "parsed"
    }

@activity.defn(name="chunk_documents_from_jsonl_activity")
async def chunk_documents_from_jsonl_activity(parsed_path: str, filename: str) -> dict:
    activity.logger.info(f"Chunking documents from {parsed_path} with filename {filename}")

    new_path = Path(parsed_path)

    upload_path = new_path.parent.parent / Path(filename).name  # path where the chunks will be upload

    chunks_path = spill_path_for_upload(upload_path, filename, "chunks")

    service = DocumentService()
    documents = []

    with new_path.open(encoding="utf-8") as f:
        for line_number, line in enumerate(f):
            text = line.strip()
            if line_number % 500 == 0:
                activity.heartbeat(f"Reading parsed jsonl line {line_number} from {parsed_path}")
            if not text:
                continue
            payload = json.loads(text)  # we are reading one json that represents one langchain document
            documents.append(Document(page_content=payload["page_content"], metadata=payload["metadata"]))

    chunks = service.split_documents(documents)
    count = write_documents_to_jsonl(chunks_path, chunks)
    line_count = count_jsonl_lines(chunks_path)
    activity.logger.info(f"Chunked {count} documents from {parsed_path} with filename {filename} to {chunks_path}")

    return {
        "chunks_count": count,
        "chunks_path": str(chunks_path),
        "line_count": line_count,
        "stage": "chunks"
    }

@activity.defn(name="index_documents_from_jsonl_activity")
async def index_documents_from_jsonl_activity(chunks_path: str, offset: int, batch_size: int) -> int:
    path = Path(chunks_path)
    batch = read_documents_from_jsonl_batch(path, offset, batch_size)
    if not batch:
        return 0

    repo = VectorStoreRepository()
    ids = repo.add_documents(batch)
    activity.heartbeat(f"Indexed {len(ids)} chunks from {chunks_path} with offset {offset} and batch size {batch_size}")
    activity.logger.info(f"Indexed {len(ids)} chunks from {chunks_path} with offset {offset} and batch size {batch_size}")
    return len(ids)

@activity.defn(name="ingest_file_activity")
async def ingest_file_activity(
    local_path: str,
    filename: str,
    batch_size: int | None = None
) -> int:
    settings = get_settings()

    batch_size = batch_size or settings.index_batch_size

    activity.logger.info(f"Ingesting file {filename} from {local_path} with batch size {batch_size}")

    def _heartbeat(indexed: int, total: int) -> None:
        activity.heartbeat(f"Indexed {indexed} of {total} chunks")

    result = IngestionService().ingest_file_at_path(
        Path(local_path),
        source_name=filename,
        index_batch_size=batch_size,
        on_index_batch=_heartbeat
    )

    return result["chunks_created"]

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
