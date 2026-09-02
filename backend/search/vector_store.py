"""
ATK Video AI Organizer - FAISS Vector Store Manager
Manages in-memory FAISS vector index for ultra-fast semantic similarity search.
"""

import numpy as np
from typing import List, Tuple, Dict, Any
from backend.database.db_manager import DatabaseManager
from backend.utils.logger import app_logger, error_logger

class LocalVectorStore:
    def __init__(self, db_manager: DatabaseManager, dim: int = 384):
        self.db = db_manager
        self.dim = dim
        self.index = None
        self.id_to_videoid = []
        self._init_index()

    def _init_index(self):
        try:
            import faiss
            self.index = faiss.IndexFlatIP(self.dim) # Inner product = cosine similarity for normalized vectors
            app_logger.info("Initialized FAISS Vector Index (IndexFlatIP)")
        except ImportError:
            app_logger.warning("FAISS not installed, using NumPy cosine similarity fallback")
            self.index = None

    def rebuild_index_from_db(self):
        """Loads all vector embeddings from SQLite database into FAISS index."""
        conn = self.db.get_connection()
        rows = conn.execute("SELECT video_id, embedding_blob, dim FROM embeddings;").fetchall()

        if not rows:
            return

        embeddings_list = []
        self.id_to_videoid = []

        for r in rows:
            vid = r["video_id"]
            blob = r["embedding_blob"]
            vec_dim = r["dim"]
            vec = np.frombuffer(blob, dtype=np.float32)
            if len(vec) == self.dim:
                embeddings_list.append(vec)
                self.id_to_videoid.append(vid)

        if embeddings_list:
            matrix = np.vstack(embeddings_list).astype(np.float32)
            if self.index is not None:
                self.index.reset()
                self.index.add(matrix)
            app_logger.info(f"Rebuilt vector index with {len(self.id_to_videoid)} videos")

    def add_embedding(self, video_id: int, vector: np.ndarray):
        """Saves vector into SQLite and adds to FAISS index."""
        if len(vector) != self.dim:
            return

        blob = vector.tobytes()
        conn = self.db.get_connection()
        conn.execute("""
            INSERT OR REPLACE INTO embeddings (video_id, vector_type, embedding_blob, dim)
            VALUES (?, 'clip', ?, ?);
        """, (video_id, blob, self.dim))
        conn.commit()

        if self.index is not None:
            self.index.add(np.expand_dims(vector, axis=0))
            self.id_to_videoid.append(video_id)

    def search_similar(self, query_vector: np.ndarray, top_k: int = 20) -> List[Tuple[int, float]]:
        """
        Searches FAISS vector store for top_k most similar videos.
        Returns list of (video_id, score) tuples.
        """
        if self.index is None or self.index.ntotal == 0:
            return self._fallback_numpy_search(query_vector, top_k)

        query_vec = np.expand_dims(query_vector.astype(np.float32), axis=0)
        scores, indices = self.index.search(query_vec, min(top_k, self.index.ntotal))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(self.id_to_videoid):
                vid = self.id_to_videoid[idx]
                results.append((vid, float(score)))

        return results

    def _fallback_numpy_search(self, query_vector: np.ndarray, top_k: int) -> List[Tuple[int, float]]:
        conn = self.db.get_connection()
        rows = conn.execute("SELECT video_id, embedding_blob FROM embeddings;").fetchall()
        results = []
        for r in rows:
            vid = r["video_id"]
            vec = np.frombuffer(r["embedding_blob"], dtype=np.float32)
            if len(vec) == len(query_vector):
                sim = float(np.dot(vec, query_vector))
                results.append((vid, sim))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
