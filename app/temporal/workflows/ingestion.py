from dataclasses import field, dataclass
from typing import Any

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from app.temporal.activities.activities import parse_documents_activity, chunk_documents_activity, index_documents_activity
    from datetime import timedelta


DEFAULT_INDEX_BATCH_SIZE = 100

@dataclass
class FileIngestInput:
    filename: str
    local_path: str

@dataclass
class BatchIngestProgress:
    status: str = "RUNNING"
    files_total: int = 0
    files_completed: int = 0
    current_filename: str | None = None
    file_results: list[dict[str, Any]] = field(default_factory=list)

@workflow.defn(name="batch-ingest-workflow")
class BatchIngestWorkflow:
    """Workflow to ingest a batch of files into the vector store."""

    def __init__(self) -> None:
        self.progress = BatchIngestProgress()

    @workflow.query
    def get_progress(self) -> BatchIngestProgress:
        return self.progress

    @workflow.run
    async def run(self, files: list[FileIngestInput]) -> BatchIngestProgress:
        """Workflow to ingest a batch of files into the vector store."""

        batch_size = DEFAULT_INDEX_BATCH_SIZE
        self.progress.files_total = len(files)
        self.progress.status = "RUNNING"

        for file_input in files:
            self.progress.current_filename = file_input.filename
            doc_dicts = await workflow.execute_activity(
                parse_documents_activity,
                args=[file_input.local_path, file_input.filename],
                start_to_close_timeout=timedelta(minutes=30),
            )

            chunk_dicts = await workflow.execute_activity(
                chunk_documents_activity,
                args=[doc_dicts],
                start_to_close_timeout=timedelta(minutes=30),
            )

            indexed = 0

            for start in range(0, len(chunk_dicts), batch_size):
                batch = chunk_dicts[start: start + batch_size]
                count = await workflow.execute_activity(
                    index_documents_activity,
                    args=[batch],
                    start_to_close_timeout=timedelta(minutes=30),
                    heartbeat_timeout=timedelta(minutes=5),
                )
                indexed += count

            self.progress.files_completed += 1
            self.progress.file_results.append({
                "filename": file_input.filename,
                "chunks_indexed": indexed,
                "document_ids": []
            })

        self.progress.status = "COMPLETED"
        self.progress.current_filename = None
        return self.progress