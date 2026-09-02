"""
ATK Video AI Organizer - Duplicate Detection Engine
Detects exact (SHA-256), near (Perceptual Hash), and semantic (Embedding) duplicates.
"""

from typing import List, Dict, Any
from backend.database.db_manager import DatabaseManager

class DuplicateFinder:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def find_all_duplicates(self) -> List[Dict[str, Any]]:
        """
        Scans all videos in database and groups duplicates into clusters.
        """
        conn = self.db.get_connection()
        videos = [dict(r) for r in conn.execute("SELECT id, original_path, filename, file_size, file_hash, phash, quality_score FROM videos;").fetchall()]

        # Clear existing duplicate entries
        conn.execute("DELETE FROM duplicates;")
        conn.commit()

        group_id = 1
        processed_ids = set()
        duplicate_groups = []

        # 1. Exact Duplicate Search (SHA-256 Hash or identical size+hash)
        hash_map = {}
        for v in videos:
            h = v["file_hash"]
            if h and len(h) > 10:
                hash_map.setdefault(h, []).append(v)

        for h, group in hash_map.items():
            if len(group) > 1:
                # Determine highest quality file to keep
                sorted_group = sorted(group, key=lambda x: (x["quality_score"], x["file_size"]), reverse=True)
                best_video = sorted_group[0]

                group_items = []
                for v in group:
                    processed_ids.add(v["id"])
                    action = "Keep (Highest Quality)" if v["id"] == best_video["id"] else "Duplicate Candidate"
                    conn.execute("""
                        INSERT INTO duplicates (group_id, video_id, duplicate_type, match_score, recommended_action)
                        VALUES (?, ?, 'exact', 1.0, ?);
                    """, (group_id, v["id"], action))
                    group_items.append({**v, "recommended_action": action})

                duplicate_groups.append({
                    "group_id": group_id,
                    "duplicate_type": "exact",
                    "videos": group_items
                })
                group_id += 1

        # 2. Near Duplicate Search (Perceptual Hash similarity)
        phash_videos = [v for v in videos if v["id"] not in processed_ids and v["phash"]]
        for i in range(len(phash_videos)):
            v1 = phash_videos[i]
            if v1["id"] in processed_ids:
                continue

            matches = [v1]
            h1_hex = v1["phash"]

            for j in range(i + 1, len(phash_videos)):
                v2 = phash_videos[j]
                if v2["id"] in processed_ids:
                    continue

                h2_hex = v2["phash"]
                # Calculate hamming distance between hex strings
                if len(h1_hex) == len(h2_hex):
                    try:
                        diff = sum(c1 != c2 for c1, c2 in zip(h1_hex, h2_hex))
                        if diff <= 4: # Small hamming distance = near duplicate
                            matches.append(v2)
                    except Exception:
                        pass

            if len(matches) > 1:
                sorted_group = sorted(matches, key=lambda x: (x["quality_score"], x["file_size"]), reverse=True)
                best_video = sorted_group[0]

                group_items = []
                for v in matches:
                    processed_ids.add(v["id"])
                    action = "Keep (Highest Quality)" if v["id"] == best_video["id"] else "Near Duplicate Candidate"
                    conn.execute("""
                        INSERT INTO duplicates (group_id, video_id, duplicate_type, match_score, recommended_action)
                        VALUES (?, ?, 'near', 0.95, ?);
                    """, (group_id, v["id"], action))
                    group_items.append({**v, "recommended_action": action})

                duplicate_groups.append({
                    "group_id": group_id,
                    "duplicate_type": "near",
                    "videos": group_items
                })
                group_id += 1

        conn.commit()
        return duplicate_groups
