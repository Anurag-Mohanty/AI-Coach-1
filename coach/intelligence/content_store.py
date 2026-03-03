"""
Content Intelligence Store — Phase C+

Indexes proven content by (use_case_category × seniority_tier), builds up from
every PRESCRIBE session, and surfaces high-performing items as warm-start candidates
for future matching sessions.

Warm-start items go through reflection before use — they are candidates, not guarantees.
The reflection agent decides fitness for the specific user's seniority, tools, and skills.

Schema:
  content/content_index.json → {
    "version": 1,
    "content": {
      "{content_id}": {
        "title", "link", "source", "format", "description",
        "categories": [...],         # can accumulate across use case contexts
        "seniority_tiers": [...],    # can accumulate across role levels
        "archetype_ids": [...],      # which role archetypes this was served to
        "session_count": N,
        "thumbs_up": N, "thumbs_down": N,
        "first_seen": ISO, "last_seen": ISO
      }
    },
    "category_index": {
      "stakeholder_alignment": {
        "director": ["content_id1", ...],
        "vp": [...]
      }
    }
  }
"""
import hashlib
import json
import os
import re
from datetime import datetime, timezone


_STORE_PATH = os.path.join(
    os.path.dirname(__file__),
    "content",
    "content_index.json",
)

# Minimum evidence required before surfacing as warm start
_MIN_SESSION_COUNT = 3


class ContentStore:
    def __init__(self, store_path: str = None):
        self._path = store_path or _STORE_PATH
        self._data = self._load()

    # ── Public API ──────────────────────────────────────────────────────────

    def record_session(
        self,
        use_case_category: str,
        seniority_tier: str,
        archetype_id: str,
        curated_items: list,
    ) -> None:
        """
        Record content items served in a PRESCRIBE session.
        Updates content records and category index. Saves to disk.
        """
        if not curated_items or not use_case_category:
            return

        now_iso = datetime.now(timezone.utc).isoformat()
        category = self._derive_category(use_case_category)
        tier = self._normalize_tier(seniority_tier)

        content_dict = self._data.setdefault("content", {})
        cat_index = self._data.setdefault("category_index", {})

        for item in curated_items:
            link = item.get("link", "")
            if not link:
                continue

            cid = self._content_id(link)

            # Upsert content record
            if cid not in content_dict:
                content_dict[cid] = {
                    "title": item.get("title", ""),
                    "link": link,
                    "source": item.get("source", ""),
                    "format": item.get("format", "Article"),
                    "description": item.get("description", "") or item.get("snippet", ""),
                    "categories": [],
                    "seniority_tiers": [],
                    "archetype_ids": [],
                    "session_count": 0,
                    "thumbs_up": 0,
                    "thumbs_down": 0,
                    "first_seen": now_iso,
                    "last_seen": now_iso,
                }

            rec = content_dict[cid]
            rec["session_count"] += 1
            rec["last_seen"] = now_iso
            # Refresh title/description if richer data available
            if item.get("title"):
                rec["title"] = item["title"]
            if item.get("description") or item.get("snippet"):
                rec["description"] = item.get("description", "") or item.get("snippet", "")

            # Accumulate category + tier + archetype associations
            if category and category not in rec["categories"]:
                rec["categories"].append(category)
            if tier and tier not in rec["seniority_tiers"]:
                rec["seniority_tiers"].append(tier)
            if archetype_id and archetype_id not in rec["archetype_ids"]:
                rec["archetype_ids"].append(archetype_id)

            # Update category index
            if category and tier:
                tier_list = cat_index.setdefault(category, {}).setdefault(tier, [])
                if cid not in tier_list:
                    tier_list.append(cid)

        self._save()

    def get_warm_start(
        self,
        use_case_category: str,
        seniority_tier: str,
        top_n: int = 5,
    ) -> list:
        """
        Return top-rated content items for this use_case_category × seniority_tier.

        Gate: item must have session_count >= 3 OR thumbs_up >= 1.
        Returns full item dicts (title, link, source, format, description) ready
        for the reflection agent to evaluate.
        """
        category = self._derive_category(use_case_category)
        tier = self._normalize_tier(seniority_tier)

        if not category or not tier:
            return []

        content_ids = (
            self._data
            .get("category_index", {})
            .get(category, {})
            .get(tier, [])
        )
        if not content_ids:
            return []

        content_dict = self._data.get("content", {})
        candidates = []
        for cid in content_ids:
            rec = content_dict.get(cid)
            if not rec:
                continue
            # Gate: proven items only
            if rec["session_count"] < _MIN_SESSION_COUNT and rec["thumbs_up"] < 1:
                continue
            candidates.append((cid, rec))

        # Sort: thumbs_up desc, then session_count desc
        candidates.sort(
            key=lambda x: (x[1]["thumbs_up"], x[1]["session_count"]),
            reverse=True,
        )

        results = []
        for _cid, rec in candidates[:top_n]:
            results.append({
                "title": rec["title"],
                "link": rec["link"],
                "source": rec["source"],
                "format": rec["format"],
                "description": rec["description"],
                "snippet": rec["description"],
                "source_tag": "content_store",  # marks warm-start origin for logging
            })
        return results

    def record_feedback(self, content_id_or_link: str, helpful: bool) -> None:
        """
        Record thumbs up/down for a content item (by link or content_id).
        Re-sorts category index for affected categories.
        """
        # Accept link or pre-hashed content_id
        if content_id_or_link.startswith("http"):
            cid = self._content_id(content_id_or_link)
        else:
            cid = content_id_or_link

        content_dict = self._data.get("content", {})
        if cid not in content_dict:
            return

        if helpful:
            content_dict[cid]["thumbs_up"] += 1
        else:
            content_dict[cid]["thumbs_down"] += 1

        self._save()

    # ── Private helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _content_id(link: str) -> str:
        """Stable 16-char ID from URL — same link always maps to same ID."""
        return hashlib.sha256(link.encode()).hexdigest()[:16]

    @staticmethod
    def _derive_category(task_cluster_or_use_case: str) -> str:
        """
        Normalize a task cluster name or use case task string to a category slug.
        "Stakeholder alignment" → "stakeholder_alignment"
        "AI for Executive Communication" → "ai_for_executive_communication"
        """
        if not task_cluster_or_use_case:
            return ""
        slug = task_cluster_or_use_case.lower()
        slug = re.sub(r"[^a-z0-9\s]", "", slug)
        slug = re.sub(r"\s+", "_", slug.strip())
        return slug[:60]  # cap length

    @staticmethod
    def _normalize_tier(seniority: str) -> str:
        """Map seniority string to tier bucket."""
        if not seniority:
            return "manager"
        s = seniority.lower().strip()
        if any(x in s for x in ["vp", "vice president", "svp", "evp"]):
            return "vp"
        if any(x in s for x in ["director", "head of"]):
            return "director"
        if any(x in s for x in ["principal", "staff", "senior"]):
            return "senior"
        if any(x in s for x in ["manager", "lead"]):
            return "manager"
        return "manager"

    def _load(self) -> dict:
        if os.path.exists(self._path):
            try:
                with open(self._path, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"version": 1, "content": {}, "category_index": {}}

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        with open(self._path, "w") as f:
            json.dump(self._data, f, indent=2)
