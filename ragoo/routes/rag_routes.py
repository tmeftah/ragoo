# RAG routes (API endpoints)
from fastapi import APIRouter, Depends, HTTPException


from ragoo.services.rag_service import rag_service
from ragoo.schemas.document import DocumentBatch
from ragoo.core.security import get_current_user

router = APIRouter()


@router.post("/query")
async def query_endpoint(query: str, user: dict = Depends(get_current_user)):
    return rag_service.process_query(query)


@router.post("/chat")
async def query_endpoint(query: str, user: dict = Depends(get_current_user)):
    return rag_service.chat(query)


@router.post("/documents")
async def add_documents(
    document_batch: DocumentBatch,
    user: dict = Depends(get_current_user),
):
    """
    Add documents to the vector store with embeddings
    Requires authentication
    """
    try:
        # Convert Pydantic model to list of (content, metadata) tuples
        documents = [(doc.content, doc.metadata) for doc in document_batch.documents]

        # Add to vector store through service
        result = rag_service.add_documents(documents)

        return {
            "message": "Documents added successfully",
            "count": result["count"],
            "document_ids": result["ids"],
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Document ingestion failed: {str(e)}"
        )
