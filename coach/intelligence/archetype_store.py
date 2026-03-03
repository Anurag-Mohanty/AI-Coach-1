"""
Role Archetype Store — Phase C intelligence moat.

JSON-backed store of role archetypes. Each record contains pre-computed
task_clusters, common_blind_spots, and aspiration patterns derived from
real session data (seeded with synthetic profiles initially).

When a user's profile matches a known archetype (score >= 0.6), the platform:
  1. Skips the infer_role_detail GPT-4o call → returns cached task_clusters
  2. Injects common_blind_spots as priors into use_case_miss_agent

Matching keys: seniority + domain + org_shape (weighted score).
Phase C+ will add ChromaDB for semantic matching of novel roles.
"""

import json
import os
from pathlib import Path

_DEFAULT_STORE_PATH = Path(__file__).parent / "archetypes" / "seed.json"

# Seniority normalization — map common variants to canonical buckets
_SENIORITY_MAP = {
    "junior": "junior",
    "associate": "junior",
    "mid": "mid",
    "manager": "mid",
    "product manager": "mid",
    "senior": "senior",
    "lead": "senior",
    "principal": "senior",
    "staff": "senior",
    "director": "director",
    "sr. director": "director",
    "senior director": "director",
    "vp": "vp",
    "vice president": "vp",
    "svp": "vp",
    "evp": "vp",
    "head of": "head",
    "head": "head",
    "chief": "chief",
    "cpo": "chief",
    "cto": "chief",
    "c-level": "chief",
}

# Domain normalization — map variants to canonical domain buckets
_DOMAIN_MAP = {
    "healthcare": "healthcare",
    "health": "healthcare",
    "clinical": "healthcare",
    "medical": "healthcare",
    "pharma": "healthcare",
    "biotech": "healthcare",
    "fintech": "fintech",
    "financial": "fintech",
    "banking": "fintech",
    "insurance": "fintech",
    "payments": "fintech",
    "saas": "saas",
    "software": "saas",
    "enterprise software": "saas",
    "b2b": "saas",
    "retail": "retail",
    "e-commerce": "retail",
    "ecommerce": "retail",
    "consumer": "retail",
    "ai": "ai",
    "ml": "ai",
    "machine learning": "ai",
    "data": "ai",
}


class RoleArchetypeStore:
    """
    Loads and queries the role archetype store.

    Usage:
        store = RoleArchetypeStore()
        archetype, score = store.find_closest("Director", "Healthcare", "hierarchical")
        if archetype and score >= 0.6:
            task_clusters = archetype["task_clusters"]
    """

    def __init__(self, store_path: str = None):
        self._path = Path(store_path) if store_path else _DEFAULT_STORE_PATH
        self._archetypes: list[dict] = []
        self._load()

    def _load(self):
        if self._path.exists():
            try:
                with open(self._path) as f:
                    self._archetypes = json.load(f)
            except Exception as e:
                print(f"[archetype_store] Failed to load {self._path}: {e}")
                self._archetypes = []
        else:
            self._archetypes = []

    def _save(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w") as f:
            json.dump(self._archetypes, f, indent=2)

    def _normalize_seniority(self, s: str) -> str:
        s = s.lower().strip()
        for key, canonical in _SENIORITY_MAP.items():
            if key in s:
                return canonical
        return s

    def _normalize_domain(self, s: str) -> str:
        s = s.lower().strip()
        for key, canonical in _DOMAIN_MAP.items():
            if key in s:
                return canonical
        return s

    def _normalize_org_shape(self, s: str) -> str:
        return s.lower().strip()

    def _score(self, archetype: dict, seniority: str, domain: str, org_shape: str) -> float:
        """
        Weighted match score:
          seniority  = 0.50 (most important — determines role scope)
          domain     = 0.35 (industry expertise)
          org_shape  = 0.15 (least discriminating at seed stage)
        """
        score = 0.0
        arch_seniority = self._normalize_seniority(archetype.get("seniority", ""))
        arch_domain = self._normalize_domain(archetype.get("domain", ""))
        arch_org_shape = self._normalize_org_shape(archetype.get("org_shape", ""))

        # Seniority — exact bucket match
        if arch_seniority == seniority:
            score += 0.50
        elif _nearby_seniority(arch_seniority, seniority):
            score += 0.25  # adjacent seniority (senior ↔ director) gets partial credit

        # Domain — exact bucket match or "any" wildcard
        if arch_domain == "any" or arch_domain == domain:
            score += 0.35
        elif _related_domain(arch_domain, domain):
            score += 0.15  # e.g. healthcare ↔ fintech are not related; saas ↔ ai are adjacent

        # Org shape — exact match
        if arch_org_shape == "any" or arch_org_shape == org_shape:
            score += 0.15

        return round(score, 3)

    def find_closest(self, seniority: str, domain: str, org_shape: str) -> tuple[dict | None, float]:
        """
        Return (best_matching_archetype, score).
        Score >= 0.6 means a reliable match — safe to use cached task_clusters.
        Score < 0.35 means seniority didn't match — return (None, 0.0).
        """
        if not self._archetypes:
            return None, 0.0

        norm_seniority = self._normalize_seniority(seniority)
        norm_domain = self._normalize_domain(domain)
        norm_org_shape = self._normalize_org_shape(org_shape)

        best = None
        best_score = 0.0
        for archetype in self._archetypes:
            s = self._score(archetype, norm_seniority, norm_domain, norm_org_shape)
            if s > best_score:
                best_score = s
                best = archetype

        if best_score < 0.35:
            return None, 0.0
        return best, best_score

    def get(self, archetype_id: str) -> dict | None:
        """Return archetype by ID, or None."""
        for a in self._archetypes:
            if a.get("archetype_id") == archetype_id:
                return a
        return None

    def save_archetype(self, archetype_id: str, record: dict):
        """Add or replace an archetype record."""
        for i, a in enumerate(self._archetypes):
            if a.get("archetype_id") == archetype_id:
                self._archetypes[i] = record
                self._save()
                return
        self._archetypes.append(record)
        self._save()

    def update_from_session(self, archetype_id: str, use_case_chosen: str):
        """
        Flywheel write: increment session_count, track use_cases_chosen.
        Called after each successful PRESCRIBE for matched archetypes.
        """
        archetype = self.get(archetype_id)
        if not archetype:
            return
        archetype["session_count"] = archetype.get("session_count", 0) + 1
        if use_case_chosen:
            chosen_list = archetype.setdefault("use_cases_chosen", [])
            chosen_list.append(use_case_chosen)
            # Keep only last 50 entries to prevent unbounded growth
            archetype["use_cases_chosen"] = chosen_list[-50:]
        self.save_archetype(archetype_id, archetype)


def _nearby_seniority(a: str, b: str) -> bool:
    """Adjacent seniority levels get partial score credit."""
    adjacency = {
        ("senior", "director"),
        ("director", "vp"),
        ("mid", "senior"),
        ("junior", "mid"),
        ("vp", "head"),
        ("head", "chief"),
        ("director", "head"),
    }
    return (a, b) in adjacency or (b, a) in adjacency


def _related_domain(a: str, b: str) -> bool:
    """Loosely adjacent domains get partial score credit."""
    adjacency = {
        ("saas", "ai"),
        ("fintech", "saas"),
    }
    return (a, b) in adjacency or (b, a) in adjacency
