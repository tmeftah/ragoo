import os
import re
import hashlib
import requests
import json
from chromadb import PersistentClient
import chromadb.utils.embedding_functions as embedding_functions

# Configuration
CHROMA_DB_PATH = "chroma_db"  # Directory to store the ChromaDB database
OLLAMA_API_URL = (
    "http://localhost:11434/api/embeddings"  # Or wherever your ollama is running
)
MODEL_NAME = (
    "nomic-embed-text"  # The ollama model you want to use (ensure it's installed)
)
MAX_CHUNK_SIZE = 2048


def read_md_file(filepath):
    """Reads a Markdown file and returns its contents as a string."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return None


def split_into_pages(text, page_separator="-----"):
    """Splits a Markdown document into pages based on the specified separator."""
    pages = text.split(page_separator)
    # Remove leading/trailing whitespace from each page
    pages = [page.strip() for page in pages]
    # Filter out empty pages
    pages = [page for page in pages if page]
    return pages


def clean_page_content(text):
    """Cleans up a page's content by removing excessive whitespace and irrelevant characters. Customization required."""
    # Remove multiple consecutive spaces
    text = re.sub(r"\s+", " ", text)
    # Remove leading/trailing whitespace
    text = text.strip()
    # Custom cleaning (e.g., remove specific markers or codes in a document
    # Example: Remove specific markers or codes in a document
    text = re.sub(
        r'<span class="latex-block"><span class="katex-display"><span class="katex"><span class="katex-mathml"><math xmlns="http://www.w3.org/1998/Math/MathML" display="block"><semantics><mrow><mi>O</mi><mi>F</mi><mi>F</mi><mi>I</mi><mi>C</mi><mi>I</mi><mi>A</mi><mi>L</mi><mi>J</mi><mi>O</mi><mi>U</mi><mi>R</mi><mi>N</mi><mi>A</mi><mi>L</mi><mi>M</mi><mi>A</mi><mi>R</mi><mi>K</mi><mi>E</mi><mi>R</mi><mo>:</mo><mi mathvariant="normal">.</mi><mo>∗</mo><mo stretchy="false">?</mo></mrow><annotation encoding="application/x-tex">OFFICIAL JOURNAL MARKER:.*?</annotation></semantics></math></span><span class="katex-html" aria-hidden="true"><span class="base"><span class="strut" style="height:0.6833em;"></span><span class="mord mathnormal" style="margin-right:0.13889em;">OFF</span><span class="mord mathnormal" style="margin-right:0.07847em;">I</span><span class="mord mathnormal" style="margin-right:0.07153em;">C</span><span class="mord mathnormal" style="margin-right:0.07847em;">I</span><span class="mord mathnormal">A</span><span class="mord mathnormal">L</span><span class="mord mathnormal" style="margin-right:0.09618em;">J</span><span class="mord mathnormal" style="margin-right:0.02778em;">O</span><span class="mord mathnormal" style="margin-right:0.10903em;">U</span><span class="mord mathnormal" style="margin-right:0.10903em;">RN</span><span class="mord mathnormal">A</span><span class="mord mathnormal">L</span><span class="mord mathnormal" style="margin-right:0.10903em;">M</span><span class="mord mathnormal">A</span><span class="mord mathnormal" style="margin-right:0.00773em;">R</span><span class="mord mathnormal" style="margin-right:0.07153em;">K</span><span class="mord mathnormal" style="margin-right:0.00773em;">ER</span><span class="mspace" style="margin-right:0.2778em;"></span><span class="mrel">:</span><span class="mspace" style="margin-right:0.2778em;"></span></span><span class="base"><span class="strut" style="height:0.6944em;"></span><span class="mord">.</span><span class="mord">∗</span><span class="mclose">?</span></span></span></span></span></span>',
        "",
        text,
    )  # Example
    return text


def create_chunks_with_overlap(
    pages, overlap=0.2
):  # Overlap as a fraction of page content
    """Creates chunks from pages, with overlap between them."""
    chunks = []
    num_pages = len(pages)

    for i in range(num_pages):
        page = pages[i]
        cleaned_page = clean_page_content(page)

        if cleaned_page:  # Only add the chunk, if the chunk is not empty
            chunks.append(
                {"page_number": i + 1, "content": cleaned_page}  # Number of page
            )

    overlapped_chunks = []

    for i in range(len(chunks)):
        current_chunk = chunks[i]
        content = current_chunk["content"]
        page_number = current_chunk["page_number"]

        if i > 0:
            previous_chunk = chunks[i - 1]
            previous_content = previous_chunk["content"]

            overlap_length = int(
                len(previous_content) * overlap
            )  # Length to use from previous page

            overlap_text = previous_content[
                -overlap_length:
            ]  # Extract content from back

            combined_content = f"{overlap_text}\n{content}"  # Combine both
        else:
            combined_content = content

        # Split the combined content into chunks of MAX_CHUNK_SIZE, if necessary
        if len(combined_content) > MAX_CHUNK_SIZE:
            split_chunks = split_text_into_chunks(combined_content, MAX_CHUNK_SIZE)
            for j, split_chunk in enumerate(split_chunks):
                chunk_id = generate_chunk_id(split_chunk)
                overlapped_chunks.append(
                    {
                        "id": f"{chunk_id}_{j}",  # Add index to avoid duplicate IDs
                        "page_number": page_number,
                        "content": split_chunk,
                    }
                )
        else:
            chunk_id = generate_chunk_id(combined_content)
            overlapped_chunks.append(
                {
                    "id": chunk_id,
                    "page_number": page_number,
                    "content": combined_content,
                }
            )

    return overlapped_chunks


def split_text_into_chunks(text, chunk_size):
    """Splits text into chunks of a specified size. Tries to split on sentences."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        # Try to split the chunk on a sentence boundary (., ?, !)
        split_point = -1
        for i in range(end - 1, start, -1):
            if text[i] in [".", "?", "!"] and text[i + 1] == " ":
                split_point = i + 1
                break

        if split_point != -1:
            end = split_point

        chunks.append(text[start:end])
        start = end
    return chunks


def generate_chunk_id(chunk_content):
    """Generates a unique ID for a chunk."""
    hash_object = hashlib.sha256(chunk_content.encode("utf-8"))
    return hash_object.hexdigest()


def ollama_embedding(text, ollama_api_url=OLLAMA_API_URL, model_name=MODEL_NAME):
    """Generates embeddings using an Ollama instance via HTTP request. No library dependencies."""
    # print(text) # Commented out to prevent excessive printing.
    try:
        payload = json.dumps({"prompt": text, "model": model_name})
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            ollama_api_url, headers=headers, data=payload, stream=False
        )  # Important: stream=False

        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        json_response = response.json()

        return json_response["embedding"]  # Extract embedding from JSON
    except requests.exceptions.RequestException as e:
        print(f"Error during Ollama request: {e}")
        return None
    except KeyError:
        print(f"Unexpected JSON response from Ollama: {json_response}")
        return None
    except Exception as e:
        print(f"General Error during embedding: {e}")
        return None


def process_md_file(filepath, overlap=0.2, collection_name="my_collection"):
    """Processes a single Markdown file, embeds chunks, and adds them to ChromaDB."""
    content = read_md_file(filepath)
    if not content:
        return

    pages = split_into_pages(content)
    overlapped_chunks = create_chunks_with_overlap(pages, overlap)

    client = PersistentClient(path=CHROMA_DB_PATH)  # Chroma client

    collection = client.get_or_create_collection(
        name=collection_name, metadata={"hnsw:space": "cosine"}
    )

    chunk_ids = []
    chunk_contents = []
    chunk_metadatas = []

    for chunk in overlapped_chunks:
        chunk_id = chunk["id"]  # Use the ID generated in create_chunks_with_overlap
        chunk["filepath"] = filepath
        chunk_ids.append(chunk_id)
        chunk_contents.append(chunk["content"])
        chunk_metadatas.append(
            {"page_number": chunk["page_number"], "source": filepath}
        )

    chunk_embeddings = [
        ollama_embedding(text) for text in chunk_contents
    ]  # Get it from ollama api call.
    chunk_embeddings = [
        emb for emb in chunk_embeddings if emb is not None
    ]  # Cleaning if there are nones, maybe due to a timeout

    # Ensure that the lengths of ids, embeddings, and metadatas match.
    ids_to_add = chunk_ids[: len(chunk_embeddings)]
    embeddings_to_add = chunk_embeddings
    metadatas_to_add = chunk_metadatas[
        : len(chunk_embeddings)
    ]  # same length as embeddings
    documents_to_add = chunk_contents[: len(chunk_embeddings)]  # add documents too.

    if not embeddings_to_add:
        print(f"No embeddings created for {filepath}!")
        return

    try:
        collection.add(
            ids=ids_to_add,
            embeddings=embeddings_to_add,
            metadatas=metadatas_to_add,
            documents=documents_to_add,
        )
        print(f"Added {len(embeddings_to_add)} chunks from {filepath} to ChromaDB")
    except Exception as e:
        print(f"Error adding chunks to ChromaDB: {e}")


def process_directory(directory, overlap=0.2, collection_name="rag_documents"):
    """Processes all Markdown files in a directory and adds them to ChromaDB.."""
    for filename in os.listdir(directory):
        if filename.endswith(".md"):
            filepath = os.path.join(directory, filename)
            process_md_file(filepath, overlap, collection_name)


def query_chromadb(query, collection_name="rag_documents", top_k=5):

    client = PersistentClient(path=CHROMA_DB_PATH)
    try:
        collection = client.get_collection(name=collection_name)
    except ValueError as e:  # Collection not found
        print(
            f"Collection '{collection_name}' not found.  Ensure data has been ingested."
        )
        return []

    query_embedding = ollama_embedding(query)
    if query_embedding is None:
        print("Failed to generate embedding for the query.")
        return []

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=[
            "metadatas",
            "documents",
            "distances",
        ],  # Added documents for easier reading of results
    )
    return results


# Example usage:
if __name__ == "__main__":
    # 1. Process a single file or directory:
    # filepath = "path/to/your/document.md"
    # process_md_file(filepath, overlap=0.2)
    directory_path = "."
    process_directory(directory_path, overlap=0.1)

    # 2. Query ChromaDB
    query = "What are the  goals for ai ?"
    results = query_chromadb(query)

    if results and "documents" in results and results["documents"]:
        print("\nQuery Results:")
        for i, document in enumerate(results["documents"][0]):
            print(f"\nResult {i+1}:")
            print(f"  Document: {document[:200]}...")  # Print first 200 characters
            print(f"  Page Number: {results['metadatas'][0][i]['page_number']}")
            print(
                f"  Filepath: {results['metadatas'][0][i]['source']}"
            )  # Changed Key name
            print(
                f"  Distance: {results['distances'][0][i]}"
            )  # Lower distance = higher similarity
            print("-" * 40)
