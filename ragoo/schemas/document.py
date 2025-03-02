# Document schemas (Pydantic)f
from pydantic import BaseModel


class DocumentCreate(BaseModel):
    content: str
    metadata: dict = {}


class DocumentBatch(BaseModel):
    documents: list[DocumentCreate]
