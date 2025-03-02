# Document schemas (Pydantic)f
from pydantic import BaseModel, ConfigDict


class DocumentCreate(BaseModel):
    content: str
    metadata: dict = {}

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "content": "Sample document text",
                "metadata": {"source": "test"},
            }
        }
    )


class DocumentBatch(BaseModel):
    documents: list[DocumentCreate]
