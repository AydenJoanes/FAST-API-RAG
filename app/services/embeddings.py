from sentence_transformers import SentenceTransformer
from typing import List


class EmbeddingService:
    """
    Wrapper around MiniLM embedding model
    """

    def __init__(self):
        # Free, lightweight embedding model
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed_text(self, text: str) -> List[float]:
        """
        Embed a single text chunk
        """
        embedding = self.model.encode(text)
        return embedding.tolist()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embed multiple chunks at once
        """
        embeddings = self.model.encode(texts)
        return embeddings.tolist()
