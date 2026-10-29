from fastapi import APIRouter, File, HTTPException, UploadFile

from app.configs.settings import get_settings
from app.schemas.api import DocumentBatchUploadresponse
from app.services.ingestion_service import IngestionService
from app.utils import get_logger


logger = get_logger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post(
    "/upload",
    summary="Upload a document to be indexed in the vector store",
    response_model=None
)
async def upload_documents(
    files: list[UploadFile] = File(..., description="The files to upload")
):
    settings = get_settings()

    if not files:
        raise HTTPException(
            status_code=400,
            detail="No files provided. At least one file is required"
        )

    if len(files) > settings.max_files_per_upload:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum number of files exceeded. Maximum is {settings.max_files_per_upload} files."
        )

    file_pairs: list[tuple[str, bytes]] = []

    for file in files:
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="File has no filename. Please provide a file with a valid filename."
            )

        content = await file.read()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="File is empty. Please provide a non-empty file."
            )

        file_pairs.append((file.filename, content))

    service = IngestionService()

    try:
        payload = service.ingest_files_sync(file_pairs)
    except ValueError as e:
        logger.error(f"Error ingesting files: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error ingesting files: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    return DocumentBatchUploadresponse(
        chunks_created=payload["chunks_created"],
        files=payload["files"],
        files_total=payload["files_total"],
        message=payload["message"]
    )