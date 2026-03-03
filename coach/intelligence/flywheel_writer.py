"""
flywheel_writer.py — Write session outcomes back to the role archetype store.

Called after each successful PRESCRIBE. Increments session_count and
tracks which use cases are chosen, building aggregate intelligence
over time without storing any PII.

Phase C: simple session_count + use_cases_chosen tracking.
Phase C+: use aggregate data to re-derive task_clusters from real usage.
"""

from coach.intelligence.archetype_store import RoleArchetypeStore

_store = RoleArchetypeStore()


def update_archetype(archetype_id: str, use_case_title: str, has_content: bool = True) -> bool:
    """
    Record that a session completed PRESCRIBE for the given archetype.

    Args:
        archetype_id: The matched archetype ID (e.g. 'director_healthcare_hierarchical').
                      If None or empty, this is a no-op.
        use_case_title: The use case the user engaged with (for popularity tracking).
        has_content: Whether content was successfully retrieved. If False, still
                     increments session_count but does not add to use_cases_chosen.

    Returns:
        True if the archetype was found and updated, False otherwise.
    """
    if not archetype_id:
        return False

    archetype = _store.get(archetype_id)
    if not archetype:
        return False

    archetype["session_count"] = archetype.get("session_count", 0) + 1

    if use_case_title and has_content:
        chosen = archetype.setdefault("use_cases_chosen", [])
        chosen.append(use_case_title)
        # Keep only last 50 to prevent unbounded growth
        archetype["use_cases_chosen"] = chosen[-50:]

    _store.save_archetype(archetype_id, archetype)
    return True


def get_top_use_cases(archetype_id: str, top_n: int = 3) -> list[str]:
    """
    Return the most frequently chosen use cases for a given archetype.
    Used in Phase C+ to pre-surface popular use cases for similar users.
    """
    archetype = _store.get(archetype_id)
    if not archetype:
        return []

    chosen = archetype.get("use_cases_chosen", [])
    if not chosen:
        return []

    # Count occurrences and return top N
    counts: dict[str, int] = {}
    for uc in chosen:
        counts[uc] = counts.get(uc, 0) + 1

    sorted_use_cases = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return [title for title, _ in sorted_use_cases[:top_n]]
