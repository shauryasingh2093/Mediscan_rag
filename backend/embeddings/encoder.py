import hashlib
import random
from typing import List, Optional

from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model: Optional[SentenceTransformer] = None
        self._use_fallback = False
        self._vector_dim = 384

        try:
            self.model = SentenceTransformer(model_name, device="cpu", local_files_only=True)
        except Exception:
            try:
                self.model = SentenceTransformer(model_name, device="cpu")
            except Exception:
                self.model = None
                self._use_fallback = True

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        cleaned_texts = [text.strip() or "." for text in texts]
        if self._use_fallback or self.model is None:
            return [self._fallback_vector(text) for text in cleaned_texts]

        embeddings = self.model.encode(cleaned_texts, convert_to_numpy=True, show_progress_bar=False)
        return [vector.tolist() for vector in embeddings]

    def embed_text(self, text: str) -> List[float]:
        return self.embed_texts([text])[0]

    def _fallback_vector(self, text: str) -> List[float]:
        seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16)
        rng = random.Random(seed)
        return [rng.random() for _ in range(self._vector_dim)]
