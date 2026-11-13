from pydantic import BaseModel, Field
from datetime import datetime

class HealthResponse(BaseModel):
    """Response for the health check endpoint."""

    status: str = Field(..., description="The status of the application,")
    timestamp: datetime = Field(..., description="The timestamp of the response.")

class DocumentBatchUploadresponse(BaseModel):
    """Response for the document batch upload endpoint."""

    chunks_created: int = Field(
        ...,
        description="The number of chunks created."
    )
    files: list[dict] = Field(
        ...,
        description="The files that were uploaded and indexed"
    )
    files_total: int = Field(
        ...,
        description="The total number of files that were uploaded."
    )
    message: str = Field(
        ...,
        description="The message from the ingestion service."
    )

class AsyncIngestionStartedResponse(BaseModel):
    """Response for the asynchronous ingestion started endpoint."""

    workflow_id: str = Field(..., description="The ID of the workflow that was started.")
    batch_id: str = Field(..., description="The ID of the batch that was started.")
    run_id: str = Field(..., description="The ID of the run that was started.")
    files_total: int = Field(..., description="The total number of files that were uploaded.")
    filenames: list[str] = Field(..., description="The filenames of the files that were uploaded.")
    message: str = Field(..., description="The message from the ingestion service.")

class IngestionStatusResponse(BaseModel):
    """Response for the ingestion status endpoint."""

    workflow_id: str = Field(..., description="The ID of the workflow that was started.")
    status: str = Field(..., description="The status of the ingestion workflow.")
    files_total: int = Field(..., description="The total number of files that were uploaded.")
    files_completed: int = Field(..., description="The number of files that have been completed.")
    current_filename: str | None = Field(..., description="The filename of the file that is currently being processed.")
    file_results: list[dict] = Field(..., description="The results of the files that have been processed.")

class SourceDocument(BaseModel):
    """A source document."""
    content: str = Field(..., description="The content of the document.")
    metadata: dict = Field(..., description="The metadata of the document.")

class QueryRequest(BaseModel):
    """Request for the query endpoint."""
    question: str = Field(..., description="The question that was asked.")
    include_sources: bool = Field(..., description="Whether to include the source in the response.")

class QueryResponse(BaseModel):
    """Response for the query endpoint."""
    question: str = Field(..., description="The question that was asked.")
    answer: str = Field(..., description="The answer to the query.")
    source: list[SourceDocument] | None = Field(
        None,
        description="Retrieved source chunks when include_sources is true; otherwise null.",
    )
    processing_time_ms: float = Field(..., description="The time it took to process the query.")