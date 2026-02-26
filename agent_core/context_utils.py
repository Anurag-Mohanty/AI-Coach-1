"""
🔧 context_utils.py
Location: agent_core/

Purpose:
--------
Builds a unified, enriched context dictionary for any agent by combining memory-based task outputs (via global_agent_memory)
and persistent persona context (via persona_context). This enables more grounded, complete, and personalized prompt construction.

Used by:
--------
- Role Ladder Agent
- Learning Path Agent
- Experiment Agent
- Any other agent needing cross-agent, user-specific context

Functions:
----------
- build_enriched_context(user_id, session_id): returns a merged dictionary of context for prompt building or inference
"""

from agent_core.global_agent_memory import get_context
from agent_core.persona_context import get_user_context, infer_missing_context


def build_enriched_context(user_id, session_id):
    task_context = get_context(user_id, session_id) or {}
    persona = get_user_context(user_id) or {}
    enriched = {**task_context, **persona}
    enriched["missing_context"] = infer_missing_context(persona)
    return enriched
