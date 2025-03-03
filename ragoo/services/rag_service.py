# RAG service logic
import uuid
import pymupdf
from ragoo.vectorestore.chroma_handler import ChromaHandler
from ragoo.services.ollama_service import OllamaHandler


class RAGService:
    def __init__(self):
        self.vectorstore = ChromaHandler()
        self.llm = OllamaHandler()

    def process_query(self, query: str):
        # Retrieve context
        results = self.vectorstore.query(query)
        sources = [
            result["metadata"]["source"] for result in results
        ]  # get the sources

        context = "\n".join([result["content"] for result in results])

        # Format prompt with context
        prompt = f"""Context: {context}
        
        Question: {query}
        
        Answare only from context.
        
        Answer:"""

        # Generate completion
        response = self.llm.generate_completion(
            prompt=prompt, temperature=0.1, max_tokens=500
        )

        return {"answer": response, "context": context, "source": sources}

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

    def process_pdf(self, pdf_content: bytes, chunk_size: int = 512, overlap: int = 64):

        # Read PDF from bytes
        pdf_document = pymupdf.open(stream=pdf_content, filetype="pdf")

        text = ""
        for page in pdf_document:
            text += page.get_text()

        # Simple character-based splitting
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            start += (
                chunk_size - overlap
            )  # Move start position with overlap consideration

        return chunks


rag_service = RAGService()
