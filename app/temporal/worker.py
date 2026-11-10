import asyncio

from temporalio.worker import Worker

from app.configs.settings import get_settings
from app.temporal.client import get_temporal_client
from app.temporal.workflows.ingestion import BatchIngestionWorkflow
from app.utils import get_logger

from app.temporal.workflows.ingestion import (
    chunk_documents_activity,
    index_documents_activity,
    parse_documents_activity,
    ingest_file_activity
)

logger = get_logger(__name__)

async def main() -> None:
    settings = get_settings()

    client = await get_temporal_client()

    worker = Worker(
        client,
        task_queue=settings.temporal_task_queue,
        workflows=[BatchIngestionWorkflow],
        activities=[
            parse_documents_activity,
            chunk_documents_activity,
            index_documents_activity,
            ingest_file_activity
        ]
    )

    logger.info(f"Temporal worker started for task queue: {settings.temporal_task_queue}")

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())