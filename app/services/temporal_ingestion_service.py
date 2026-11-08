from dataclasses import asdict

from app.configs.settings import get_settings
from app.services.ingestion_service import IngestionService
from app.temporal.client import get_temporal_client
from app.temporal.workflows.ingestion import FileIngestInput, BatchIngestionWorkflow
from app.utils import get_logger

logger = get_logger(__name__)

class TemporalIngestionService:
    """Service to handle ingestion of files into the vector store using Temporal workflows."""

    def __init__(self):
        self.settings = get_settings()
        self.ingesting_service = IngestionService()

    async def start_batch_ingestion(self, file_pairs: list[tuple[str, bytes]]) -> dict:
        batch_id, paths = self.ingesting_service.save_upload_batch(file_pairs)

        files = [
            FileIngestInput(filename=path.name, local_path=str(path))
            for path in paths
        ]

        client = await get_temporal_client()
        handle = await client.start_workflow(
            BatchIngestionWorkflow.run,
            files,
            id=f"batch-ingestion-{batch_id}",
            task_queue=self.settings.temporal_task_queue,
        )

        logger.info(f"Started batch ingestion workflow with ID: {handle.run_id}")

        return {
            "message": "Batch ingestion workflow started successfully.",
            "workflow_id": handle.id,
            "run_id": handle.result_run_id,
            "batch_id": batch_id,
            "files_total": len(files),
            "filenames": [file.filename for file in files],
        }

    async def get_ingestion_status(self, workflow_id: str) -> dict:
        client = await get_temporal_client()
        handle = await client.get_workflow_handle(workflow_id)

        progress = None

        try:
            progress = await handle.query(BatchIngestionWorkflow.get_progress)
        except Exception:
            progress = None

        if progress:
            data = asdict(progress)
            return {
                "workflow_id": workflow_id,
                "status": data.get("status", "UNKNOWN"),
                "files_total": data.get("files_total", 0),
                "files_completed": data.get("files_completed", 0),
                "current_filename": data.get("current_filename"),
                "file_results": data.get("file_results", []),
            }

        return {
            "workflow_id": workflow_id,
            "status": "UNKNOWN",
            "files_total": 0,
            "files_completed": 0,
            "current_filename": None,
            "file_results": [],
        }