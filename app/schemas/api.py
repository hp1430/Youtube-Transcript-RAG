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