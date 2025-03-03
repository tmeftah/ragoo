# Logic to implement vector database using chroma
import uuid
from typing import List
import chromadb
from chromadb.utils.embedding_functions import EmbeddingFunction
import requests
from ragoo.core.config import settings


class ChromaHandler:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        self.embedding_function = OllamaEmbeddingFunction(
            host=settings.OLLAMA_HOST, model=settings.EMBEDDING_MODEL
        )

        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=self.embedding_function,
        )

    def add_documents(self, documents: list[str], metadata: list[dict]):
        """Store documents with automatic embedding generation"""
        """Handle empty metadata gracefully"""
        # Ensure metadata has same length as documents
        processed_metadata = []
        for meta in metadata:
            # Add default values if metadata is empty
            if not meta:
                processed_metadata.append({"source": "unknown"})
            else:
                processed_metadata.append(meta)

        ids = [str(uuid.uuid4()) for _ in documents]
        self.collection.add(ids=ids, documents=documents, metadatas=processed_metadata)
        return ids

    def query(self, query_text: str, k: int = 4) -> list[dict]:
        results = self.collection.query(query_texts=[query_text], n_results=k)

        return [
            {"content": doc, "metadata": meta}
            for doc, meta in zip(results["documents"][0], results["metadatas"][0])
        ]


class OllamaEmbeddingFunction(EmbeddingFunction):
    def __init__(self, host: str, model: str):
        self.host = host
        self.model = model

    def __call__(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            response = requests.post(
                f"{self.host}/api/embeddings",
                json={"model": self.model, "prompt": text},
            )
            response.raise_for_status()
            embeddings.append(response.json()["embedding"])
        return embeddings
