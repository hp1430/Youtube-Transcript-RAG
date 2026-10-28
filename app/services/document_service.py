import csv
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.utils import get_logger
from app.configs.settings import Settings

logger = get_logger(__name__)

class DocumentService:
    """Service for document processing."""

    SUPPORTED_FILE_EXTENSIONS = {".csv"}

    TRANSCRIPT_CSV_FIELDNAMES = {
        "id",
        "start",
        "end",
        "url",
        "channel_id",
        "title",
        "published",
        "text",
    }

    def __init__(self, chunk_size: int | None = None, chunk_overlap: int | None = None) :
        settings = Settings()
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = self.chunk_size,
            chunk_overlap = self.chunk_overlap,
            separators = ["\n\n", "\n", " ", ""],
            length_function = len,
        )

    def _is_transcript_csv(self, file_path: Path) -> bool:
        with file_path.open(newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            if not reader.fieldnames:
                return False
            fields = set[str](reader.fieldnames)
            return self.TRANSCRIPT_CSV_FIELDNAMES.issubset(fields) and len(fields) == len(self.TRANSCRIPT_CSV_FIELDNAMES)

    def load_transcript_csv(self, file_path: Path, source_name: str) -> list[Document]:
        """Load a transcript csv file into a list of documents."""
        documents: list[Document] = []

        with file_path.open(newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                text = row.get("text", "").strip()
                if not text:
                    continue
                metadata = {
                    "source": source_name,
                    "id": row.get("id", ""),
                    "start": row.get("start", ""),
                    "end": row.get("end", ""),
                    "url": row.get("url", ""),
                    "channel_id": row.get("channel_id", ""),
                    "title": row.get("title", ""),
                    "published": row.get("published", ""),
                }

                documents.append(Document(page_content=text, metadata=metadata))

            logger.info(f"Loaded {len(documents)} documents from {file_path}")

            return documents

    def split_documents(self, documents: list[Document]) -> list[Document]:
        return self.text_splitter.split_documents(documents)