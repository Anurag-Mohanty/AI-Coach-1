"""
infer_cultural_tone tool — wraps cultural_alignment_agent.
Returns cultural_profile_tag and tone_style so the coordinator
can adapt its voice to match how this person thinks and communicates.
"""
from tools.cultural_alignment_agent.cultural_alignment_agent import run_cultural_alignment_agent


def infer_cultural_tone(
    user_id: str,
    session_id: str,
    company: str = "",
    domain: str = "",
    seniority: str = "",
    org_shape: str = "",
    tools_known: list = None,
) -> dict:
    """
    Infer cultural tone and communication preferences from role context signals.
    Input:  role context signals (no explicit work_style question asked yet)
    Output: {cultural_profile_tag, tone_style, learning_style} or {error}
    """
    # Build context_inputs from what we know about the role so far
    # cultural_alignment_agent requires: ethnicity, work_style, collab_pattern, tone_preference
    # We infer these from domain/org signals rather than asking explicit questions

    # Map org signals to tone indicators
    formal_domains = {"healthcare", "financial services", "insurance", "banking", "government", "legal"}
    is_formal = any(d.lower() in domain.lower() for d in formal_domains) if domain else False

    hierarchical_orgs = {"large", "enterprise", "corporate", "hierarchical"}
    is_hierarchical = any(o.lower() in org_shape.lower() for o in hierarchical_orgs) if org_shape else False

    context_inputs = {
        "ethnicity": "",          # Not collected — cultural agent uses this for tone, we leave blank
        "work_style": "goal-focused" if is_formal else "collaborative",
        "collab_pattern": "async" if is_hierarchical else "sync",
        "tone_preference": "formal" if is_formal else "conversational",
        "domain": domain,
        "company": company,
        "seniority": seniority,
    }

    result = run_cultural_alignment_agent(user_id, session_id, context_inputs)

    if "error" in result:
        return result

    output = result.get("output") or result
    return {
        "cultural_profile_tag": output.get("cultural_profile_tag", "balanced"),
        "tone_style": output.get("learning_tone_profile", {}).get("tone_style", "balanced"),
        "learning_style": output.get("learning_tone_profile", {}).get("analogy_style", "outcome-driven"),
        "working_style_summary": output.get("working_style_summary", ""),
    }
