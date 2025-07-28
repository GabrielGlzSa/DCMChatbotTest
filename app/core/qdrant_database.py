from pathlib import Path
from functools import lru_cache
import os

from langchain.vectorstores import Qdrant
from langchain.schema import Document

from app.core.embeddings import get_embedding_function

embedding_function = get_embedding_function()

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

@lru_cache(maxsize=1)
def get_qdrant_retriever():
    """
    Initialize and return a Qdrant retriever with documents loaded from the specified directory.
    """
    # Ensure the embedding function is set
    if not embedding_function:
        raise ValueError("Embedding function is not set. Please configure it before initializing the retriever.")

    # Load all .txt files into a list of documents
    text_files = list(Path("./app/data/documents/").rglob("*.txt"))
    documents = []
    for file in text_files:
        text = file.read_text(encoding="utf-8")
        documents.append(Document(page_content=text, metadata={"source": str(file)}))

    qdrant = Qdrant.from_documents(
        documents=documents,
        embedding=embedding_function,
        url=QDRANT_URL,
        collection_name="services_docs"
    )

    return qdrant.as_retriever()

