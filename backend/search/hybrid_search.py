"""
ATK Video AI Organizer - Hybrid Semantic & Natural Language Search Engine
Combines Keyword matching + FAISS Vector Similarity + Structured Filters + Explainable Match Reasons.
"""

import re
from typing import List, Dict, Any
from backend.database.db_manager import DatabaseManager
from backend.models.embedding_model import LocalEmbeddingGenerator
from backend.search.vector_store import LocalVectorStore

class HybridSearchEngine:
    def __init__(self, db_manager: DatabaseManager, embedding_gen: LocalEmbeddingGenerator, vector_store: LocalVectorStore):
        self.db = db_manager
        self.embedding_gen = embedding_gen
        self.vector_store = vector_store

    def parse_natural_query(self, query: str) -> dict:
        """Parses natural language queries like 'find videos from 2024 containing motorcycles at night'."""
        filters = {}
        cleaned_query = query.lower()

        # Year filter
        year_match = re.search(r'\b(20\d\d)\b', cleaned_query)
        if year_match:
            filters["year"] = year_match.group(1)

        # Environment / Time of day
        if "night" in cleaned_query or "dark" in cleaned_query:
            filters["environment"] = "night"
        elif "day" in cleaned_query or "sunny" in cleaned_query:
            filters["environment"] = "daytime"

        # Duration filter
        if "short" in cleaned_query:
            filters["max_duration"] = 30
        elif "long" in cleaned_query:
            filters["min_duration"] = 60

        return {
            "cleaned_query": cleaned_query,
            "filters": filters
        }

    def search(self, query: str, filters: Dict[str, Any] = None, top_k: int = 50) -> List[Dict[str, Any]]:
        """
        Executes hybrid search across database text fields & FAISS vector embeddings.
        Returns videos with relevance match scores & match explanations.
        """
        if not query or not query.strip():
            # If empty query, return all videos with current filters
            videos = self.db.get_all_videos(limit=top_k)
            for v in videos:
                v["match_score"] = 100
                v["match_reasons"] = ["Browse All"]
            return videos

        parsed = self.parse_natural_query(query)
        q_text = parsed["cleaned_query"]
        q_filters = parsed["filters"]
        if filters:
            q_filters.update(filters)

        # 1. Compute query embedding vector & search FAISS vector store
        query_vec = self.embedding_gen.encode_text(q_text)
        vector_results = dict(self.vector_store.search_similar(query_vec, top_k=100))

        # 2. Get candidate videos from SQLite
        all_videos = self.db.get_all_videos(limit=500)

        results = []
        for v in all_videos:
            vid = v["id"]
            relevance = 0.0
            reasons = []

            # Check Vector similarity score (0.0 to 1.0)
            vec_sim = vector_results.get(vid, 0.0)
            if vec_sim > 0.3:
                relevance += vec_sim * 50.0
                reasons.append(f"Semantic description match ({int(vec_sim*100)}%)")

            # Check Keyword match in filename, AI description, category, tags
            text_corpus = f"{v['filename']} {v['ai_description']} {v['category']} {v['tags_csv']}".lower()
            query_words = [w for w in q_text.split() if len(w) > 2]
            
            matched_words = [w for w in query_words if w in text_corpus]
            if matched_words:
                keyword_score = (len(matched_words) / float(len(query_words))) * 40.0
                relevance += keyword_score
                reasons.append(f"Contains keywords: {', '.join(matched_words)}")

            # Check Transcripts & OCR in sub-tables
            conn = self.db.get_connection()
            trans_row = conn.execute("SELECT text FROM transcripts WHERE video_id = ? AND text LIKE ?;", (vid, f"%{q_text}%")).fetchone()
            if trans_row:
                relevance += 30.0
                reasons.append(f"Speech transcript match: '{trans_row['text'][:40]}...'")

            ocr_row = conn.execute("SELECT text FROM ocr WHERE video_id = ? AND text LIKE ?;", (vid, f"%{q_text}%")).fetchone()
            if ocr_row:
                relevance += 25.0
                reasons.append(f"Screen text (OCR) match: '{ocr_row['text'][:40]}...'")

            # Apply structured filter constraints
            if q_filters.get("year") and q_filters["year"] not in v.get("creation_date", ""):
                continue

            if q_filters.get("category") and q_filters["category"] != v.get("category"):
                continue

            if q_filters.get("max_duration") and v.get("duration", 0) > q_filters["max_duration"]:
                continue

            if q_filters.get("min_duration") and v.get("duration", 0) < q_filters["min_duration"]:
                continue

            if relevance > 15.0 or matched_words:
                match_score = int(min(100, max(1, relevance)))
                results.append({
                    **v,
                    "match_score": match_score,
                    "match_reasons": reasons if reasons else ["General relevance"]
                })

        results.sort(key=lambda x: x["match_score"], reverse=True)
        return results[:top_k]
