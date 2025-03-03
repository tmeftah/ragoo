# RAG routes (API endpoints)
from fastapi import APIRouter, Depends, HTTPException, UploadFile


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


@router.post("/upload")
async def upload_pdf(file: UploadFile, user: dict = Depends(get_current_user)):
    try:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Invalid file type")

        # Read file content
        pdf_content = await file.read()

        # Process and chunk PDF (using service)
        chunks = rag_service.process_pdf(pdf_content)

        # Add documents (chunks) to vector store
        result = rag_service.add_documents(
            [(chunk, {"source": file.filename}) for chunk in chunks]
        )

        return {
            "message": "PDF uploaded and processed",
            "chunks_count": len(chunks),
            "document_ids": result["ids"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")
