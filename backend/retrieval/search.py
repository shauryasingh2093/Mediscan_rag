from pathlib import Path
from typing import List, Dict

from backend.embeddings import EmbeddingModel
from backend.vector_db import ChromaVectorStore

VECTOR_DB_DIR = Path(__file__).resolve().parents[1] / "vector_db"


def search(query: str, collection_name: str = "medical_reports", n_results: int = 5) -> Dict:
    embedder = EmbeddingModel()
    query_embedding = embedder.embed_text(query)
    store = ChromaVectorStore(VECTOR_DB_DIR, collection_name=collection_name)
    response = store.query(query_embedding=query_embedding, n_results=n_results)

    documents = []
    for doc_id, doc, metadata, score in zip(
        response["ids"][0],
        response["documents"][0],
        response["metadatas"][0],
        response["distances"][0],
    ):
        documents.append({
            "id": doc_id,
            "text": doc,
            "metadata": metadata,
            "score": score,
        })

    return {
        "query": query,
        "results": documents,
        "collection": collection_name,
    }
