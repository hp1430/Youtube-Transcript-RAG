from time import time

from fastapi import APIRouter, HTTPException

from app.schemas.api import QueryRequest, QueryResponse, SourceDocument
from app.services.rag_query_service import RAGQueryService
from app.utils import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/query",
    tags=["query"]
)

@router.get(
    "/",
    summary="Query the vector store",
    response_model=QueryResponse
)
async def query(request: QueryRequest):
    start = time()
    rag = RAGQueryService()

    try:
        if request.include_sources:
            result = await rag.aquery_with_source(request.question)
            source = [SourceDocument(**doc) for doc in result["source"]]
        else:
            result = await rag.aquery(request.question)
            source = None
        processing_time_ms = (time() - start) * 1000

        return QueryResponse(
            question=request.question,
            answer=result["answer"],
            source=source,
            processing_time_ms=processing_time_ms
        )

    except Exception as e:
        logger.error(f"Error querying the vector store: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) from e