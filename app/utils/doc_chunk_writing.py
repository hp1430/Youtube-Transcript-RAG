import json
from pathlib import Path
from sqlite3 import connect

from langchain_core.documents import Document


def staging_dir_for_upload(upload_path: Path) -> Path:
    directory = upload_path.parent / "staging"
    directory.mkdir(parents=True, exist_ok=True)
    return directory

def spill_path_for_upload(upload_path: Path, filename: str, stage: str) -> Path:
    stem = Path(filename).stem
    return staging_dir_for_upload(upload_path) / f"{stem}.{stage}.jsonl"

def write_documents_to_jsonl(path: Path, documents: list[Document]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0

    with path.open("w", encoding="utf-8") as f:
        for doc in documents:
            record = {"page_content": doc.page_content, "metadata": doc.metadata}
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1

    return count

def read_documents_from_jsonl_batch(path: Path, offset: int, limit: int) -> list[Document]:
    documents = []

    if limit <= 0:
        limit = 10
    with path.open(encoding="utf-8") as f:
        for line_number, line in enumerate(f):
            if line_number < offset:
                continue
            if len(documents) >= limit:
                break
            text = line.strip()
            if not text:
                continue
            payload = json.loads(text)
            documents.append(Document(page_content=payload["page_content"], metadata=payload["metadata"]))

    return documents

def count_jsonl_lines(path: Path) -> int:
    with path.open(encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())