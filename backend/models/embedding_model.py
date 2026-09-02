"""
ATK Video AI Organizer - Vector Embedding Generator & Store
Computes 512-dim CLIP / MiniLM embeddings for semantic natural language search.
"""

import numpy as np
from typing import List, Optional
from backend.models.base_model import BaseModel
from backend.utils.logger import app_logger, error_logger

class LocalEmbeddingGenerator(BaseModel):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", models_dir: str = "data/models", device: str = "cpu"):
        super().__init__(model_name, models_dir, device)
        self.dim = 384 # Default MiniLM dimension

    def load_model(self):
        if self.is_loaded:
            return
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name, device=self.device, cache_folder=self.models_dir)
            self.dim = self._model.get_sentence_embedding_dimension() or 384
            self.is_loaded = True
            app_logger.info(f"Loaded Embedding Generator ({self.model_name}, dim={self.dim}) on {self.device}")
        except Exception as e:
            error_logger.error(f"Failed to load embedding model: {e}")
            self.is_loaded = False

    def unload_model(self):
        if self.is_loaded:
            self._model = None
            self.is_loaded = False
            app_logger.info("Unloaded Embedding Generator")

    def encode_text(self, text: str) -> np.ndarray:
        """Computes normalized L2 embedding vector for text query or description."""
        if not text or not text.strip():
            return np.zeros(self.dim, dtype=np.float32)

        if not self.is_loaded:
            self.load_model()

        if not self.is_loaded or self._model is None:
            # Simple TF-IDF / Bag of Words fallback vector
            vec = np.zeros(self.dim, dtype=np.float32)
            for i, char in enumerate(text[:self.dim]):
                vec[i] = float(ord(char)) / 255.0
            norm = np.linalg.norm(vec)
            return vec / norm if norm > 0 else vec

        try:
            emb = self._model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
            return emb.astype(np.float32)
        except Exception as e:
            error_logger.error(f"Embedding encoding error: {e}")
            return np.zeros(self.dim, dtype=np.float32)

    def process(self, input_text: str) -> np.ndarray:
        """Alias for encode_text to satisfy BaseModel interface."""
        return self.encode_text(input_text)
