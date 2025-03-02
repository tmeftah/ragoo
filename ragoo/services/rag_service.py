# RAG service logic
import uuid
from ragoo.vectorestore.chroma_handler import ChromaHandler
from ragoo.services.ollama_service import OllamaHandler


class RAGService:
    def __init__(self):
        self.vectorstore = ChromaHandler()
        self.llm = OllamaHandler()

    def process_query(self, query: str):
        # Retrieve context
        context = self.vectorstore.query(query)

        # Format prompt with context
        prompt = f"""Context: {context}
        
        Question: {query}
        
        Answare only from context.
        
        Answer:"""

        # Generate completion
        response = self.llm.generate_completion(
            prompt=prompt, temperature=0.1, max_tokens=500
        )

        return {"answer": response, "context": context}

    def chat(self, query: str):
        prompt = f"""Context: {query}"""
        response = self.llm.generate_completion(
            prompt=prompt, temperature=0.7, max_tokens=500
        )
        return {"answer": response, "context": query}

    def add_documents(self, documents: list[tuple[str, dict]]):
        """Process and store documents with embeddings"""
        try:
            # Split documents into content and metadata
            contents, metadatas = zip(*documents)

            # Add to vector store
            self.vectorstore.add_documents(
                documents=list(contents), metadata=list(metadatas)
            )

            # In a real implementation, return actual IDs from Chroma
            return {
                "count": len(documents),
                "ids": [str(uuid.uuid4()) for _ in documents],  # Mock IDs
            }
        except Exception as e:
            raise RuntimeError(f"Document storage failed: {str(e)}")


rag_service = RAGService()
