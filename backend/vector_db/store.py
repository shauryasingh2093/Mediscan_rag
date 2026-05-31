from pathlib import Path
from typing import Dict, List, Optional

import chromadb
from chromadb.config import Settings


class ChromaVectorStore:
    def __init__(self, persist_dir: Path, collection_name: str = "medical_reports"):
        self.persist_dir = persist_dir
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.Client(
            Settings(persist_directory=str(self.persist_dir), is_persistent=True, anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_documents(
        self,
        ids: List[str],
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict]] = None,
    ):
        self.collection.add(
            documents=texts,
            metadatas=metadatas or [{}] * len(texts),
            ids=ids,
            embeddings=embeddings,
        )

    def query(self, query_embedding: List[float], n_results: int = 5):
        return self.collection.query(query_embeddings=[query_embedding], n_results=n_results)

    def get_collection_name(self) -> str:
        return self.collection.name
