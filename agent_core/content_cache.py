
from typing import Dict, List, Optional
import os
import json
from datetime import datetime
import hashlib
from collections import defaultdict

class ContentCache:
    def __init__(self, cache_dir="logs/content_cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.metadata_index = self._load_metadata_index()
        self.feedback_index = self._load_feedback_index()

    def _load_metadata_index(self) -> Dict:
        index_path = os.path.join(self.cache_dir, "metadata_index.json")
        if os.path.exists(index_path):
            with open(index_path, "r") as f:
                return json.load(f)
        return {
            "skills": defaultdict(list),
            "tools": defaultdict(list), 
            "domains": defaultdict(list),
            "roles": defaultdict(list),
            "subtasks": defaultdict(list)
        }

    def _load_feedback_index(self) -> Dict:
        index_path = os.path.join(self.cache_dir, "feedback_index.json")
        if os.path.exists(index_path):
            with open(index_path, "r") as f:
                return json.load(f)
        return defaultdict(list)

    async def store_content(self, items: List[Dict], metadata: Dict, subtask: str = None):
        """Store content with rich metadata and context"""
        cache_key = self._generate_cache_key(metadata)
        
        # Update metadata index with broader context.
        # Use .setdefault() — the index may be a plain dict (loaded from JSON),
        # not a defaultdict, so missing keys would KeyError without the guard.
        for skill in metadata.get("missing_skills", []):
            self.metadata_index["skills"].setdefault(skill, []).append(cache_key)
        for tool in metadata.get("tool_familiarity", []):
            self.metadata_index["tools"].setdefault(tool, []).append(cache_key)
        if "domain" in metadata:
            self.metadata_index["domains"].setdefault(metadata["domain"], []).append(cache_key)
        if "seniority" in metadata:
            self.metadata_index["roles"].setdefault(metadata["seniority"], []).append(cache_key)
        if subtask:
            self.metadata_index["subtasks"].setdefault(subtask, []).append(cache_key)

        # Store content with full context
        cache_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata,
            "subtask": subtask,
            "items": items,
            "feedback": []  # Will store thumbs up/down history
        }
        
        filepath = os.path.join(self.cache_dir, f"{cache_key}.json")
        with open(filepath, "w") as f:
            json.dump(cache_entry, f)
        
        self._save_metadata_index()

    def store_feedback(self, content_id: str, was_helpful: bool):
        """Store feedback for future relevance scoring"""
        self.feedback_index[content_id].append({
            "helpful": was_helpful,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        index_path = os.path.join(self.cache_dir, "feedback_index.json")
        with open(index_path, "w") as f:
            json.dump(self.feedback_index, f)

    def get_feedback_score(self, content_id: str) -> float:
        """Get historical feedback score"""
        feedbacks = self.feedback_index.get(content_id, [])
        if not feedbacks:
            return 0.5  # Neutral score for no feedback
        
        positive = sum(1 for f in feedbacks if f["helpful"])
        return positive / len(feedbacks)

    async def search_cached_content(self, query_metadata: Dict, subtask: str = None, limit: int = 3) -> List[Dict]:
        """Search cache using metadata matching with feedback boost"""
        relevant_keys = set()
        
        # Find relevant cache keys from index
        # Use .get() with defaults — metadata_index may be a plain dict (loaded from JSON),
        # not a defaultdict, so missing keys would KeyError without the guard.
        skills_idx = self.metadata_index.get("skills", {})
        tools_idx = self.metadata_index.get("tools", {})
        domains_idx = self.metadata_index.get("domains", {})
        subtasks_idx = self.metadata_index.get("subtasks", {})

        for skill in query_metadata.get("missing_skills", []):
            relevant_keys.update(skills_idx.get(skill, []))
        for tool in query_metadata.get("tool_familiarity", []):
            relevant_keys.update(tools_idx.get(tool, []))
        if "domain" in query_metadata:
            relevant_keys.update(domains_idx.get(query_metadata["domain"], []))
        if subtask:
            relevant_keys.update(subtasks_idx.get(subtask, []))

        # Collect and score cached content
        all_results = []
        for key in relevant_keys:
            filepath = os.path.join(self.cache_dir, f"{key}.json")
            if os.path.exists(filepath):
                with open(filepath, "r") as f:
                    cache_entry = json.load(f)
                    for item in cache_entry["items"]:
                        item["cached"] = True
                        item["cache_date"] = cache_entry["timestamp"]
                        # Boost score based on feedback
                        feedback_score = self.get_feedback_score(item.get("id", ""))
                        item["relevance_score"] = (item.get("score", 1.0) + feedback_score) / 2
                        all_results.append(item)

        # Sort by relevance and limit results
        all_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        limited_results = all_results[:limit]
        print(f"\n📦 Cache search results:")
        print(f"- Found {len(all_results)} total cached items")
        print(f"- Returning {len(limited_results)} most relevant cached items")
        return limited_results

    def _generate_cache_key(self, metadata: Dict) -> str:
        """Generate unique cache key from metadata"""
        key_str = json.dumps(metadata, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()[:16]

    def _save_metadata_index(self):
        index_path = os.path.join(self.cache_dir, "metadata_index.json")
        with open(index_path, "w") as f:
            json.dump(self.metadata_index, f)
