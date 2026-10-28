from pathlib import Path
import uuid

from app.configs.settings import get_settings
from app.repositories.vector_store_repository import VectorStoreRepository
from app.services.document_service import DocumentService
from app.utils import get_logger

logger = get_logger(__name__)

class IngestionService:
    def __init__(self):
        self.settings = get_settings()
        self.document_service = DocumentService()
        self.vector_store_repository = VectorStoreRepository()

    def save_upload_batch(self, file_pairs: list[tuple[str, bytes]]) -> tuple[str, list[Path]]:
        """Save a batch of files to the upload directory."""
        batch_id = str(uuid.uuid4())
        batch_dir = Path(self.settings.upload_dir) / batch_id
        batch_dir.mkdir(parents=True, exist_ok=True)

        paths: list[Path] = []

        for filename, content in file_pairs:
            safe_name = Path(filename).name
            dest = batch_dir / safe_name
            dest.write_bytes(content)
            paths.append(dest)
            logger.info(f"Saved {filename} to {dest}")

        return batch_id, paths

    def ingest_file_at_path(self, file_path: Path, source_name: str | None = None) -> dict:
        name = source_name or file_path.name
        chunks = self.document_service.process_file(file_path, source_name=name)
        if not chunks:
            return {"filename": name, "chunks_created": 0, "document_ids": []}

        ids = self.vector_store_repository.add_documents(chunks)
        return {
            "filename": name,
            "chunks_created": len(chunks),
            "document_ids": ids
        }

    def ingest_files_sync(self, file_pairs: list[tuple[str, bytes]]) -> dict:
        _, paths = self.save_upload_batch(file_pairs)
        results = []

        for path in paths:
            results.append(self.ingest_file_at_path(path))

        total_chunks = sum(result["chunks_created"] for result in results)

        return {
            "chunks_created": total_chunks,
            "files": results,
            "files_total": len(results),
            "message": "Documents uploaded and indexed successfully"
        }