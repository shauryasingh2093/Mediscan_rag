from pathlib import Path
from typing import Dict, List

from backend.embeddings import EmbeddingModel
from backend.vector_db import ChromaVectorStore

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
VECTOR_DB_DIR = Path(__file__).resolve().parents[1] / "vector_db"

_EMBEDDER: EmbeddingModel | None = None
_VECTOR_STORE_CACHE: Dict[str, ChromaVectorStore] = {}


def get_embedder() -> EmbeddingModel:
    global _EMBEDDER
    if _EMBEDDER is None:
        _EMBEDDER = EmbeddingModel()
    return _EMBEDDER


def get_vector_store(collection_name: str = "medical_reports") -> ChromaVectorStore:
    global _VECTOR_STORE_CACHE
    if collection_name not in _VECTOR_STORE_CACHE:
        _VECTOR_STORE_CACHE[collection_name] = ChromaVectorStore(VECTOR_DB_DIR, collection_name=collection_name)
    return _VECTOR_STORE_CACHE[collection_name]


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    text = text.strip()
    if not text:
        return []

    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(text):
            break
        start = max(0, end - overlap)

    return chunks


def ingest_text(identifier: str, text: str, metadata: Dict = None, collection_name: str = "medical_reports") -> Dict:
    if not text or not text.strip():
        raise ValueError("Text must not be empty for ingestion.")

    chunks = chunk_text(text)
    if not chunks:
        raise ValueError("No text chunks could be extracted from the input document.")

    embeddings = get_embedder().embed_texts(chunks)
    ids = [f"{identifier}-{i}" for i in range(len(chunks))]
    metadatas = [
        {"source": identifier, "chunk_index": i, **(metadata or {})}
        for i in range(len(chunks))
    ]

    vector_store = get_vector_store(collection_name=collection_name)
    vector_store.add_documents(ids=ids, texts=chunks, embeddings=embeddings, metadatas=metadatas)

    return {
        "source": identifier,
        "chunks": len(chunks),
        "collection": vector_store.get_collection_name(),
    }
