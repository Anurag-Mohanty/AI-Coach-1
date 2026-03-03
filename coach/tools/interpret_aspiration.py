"""
interpret_aspiration tool — wraps aspiration_agent.interpret_aspiration().
Converts a raw user aspiration statement into structured goal intelligence:
5 realistic trajectory options, realism score, aspiration category.
"""
import asyncio

from agent_core.global_agent_memory import store_memory_sync
from agents.skill_assessment_agent.aspiration_agent import interpret_aspiration as _interpret


def interpret_aspiration(
    user_id: str,
    session_id: str,
    aspiration_statement: str,
    profile: dict = None,
) -> dict:
    """
    Interpret a stated aspiration into structured career goal intelligence.
    Input:  aspiration_statement — what the user said they want
            profile — user_model.profile dict (resume fields + role_context + role_detail)
    Output: {target_role_archetype, aspiration_category, realistic_trajectory_options,
             realism_score, role_delta_summary} or {error}
    """
    profile = profile or {}

    # Build the input dicts aspiration_agent expects
    resume_data = {
        "title": profile.get("title", ""),
        "seniority": profile.get("seniority", ""),
        "company": profile.get("company", ""),
        "domain": profile.get("domain", ""),
        "skills": profile.get("skills", []),
        "experience": profile.get("experience", ""),
        "aspiration_statement": aspiration_statement,
    }
    linkedin_data = {}  # Not collected yet

    role_detail = profile.get("role_detail", {})
    role_context = profile.get("role_context", {})

    # Write profile to session memory so aspiration_agent can read it if needed
    store_memory_sync(
        "coordinator",
        user_id,
        session_id,
        subtask_id="user_profile",
        function="interpret_aspiration_setup",
        input_fields=profile,
        output_fields={},
    )

    _args = dict(
        user_id=user_id,
        session_id=session_id,
        resume_data=resume_data,
        linkedin_data=linkedin_data,
        role_detail=role_detail,
        role_context=role_context,
    )
    try:
        result = asyncio.run(_interpret(**_args))
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(_interpret(**_args))
        finally:
            loop.close()

    if "error" in result:
        return result

    return {
        "target_role_archetype": result.get("target_role_archetype", ""),
        "target_company_type": result.get("target_company_type", ""),
        "target_domain": result.get("target_domain", ""),
        "target_org_context": result.get("target_org_context", ""),
        "aspiration_category": result.get("aspiration_category", ""),
        "realistic_trajectory_options": result.get("realistic_trajectory_options", []),
        "realism_score": result.get("realism_score", 0.7),
        "role_delta_summary": result.get("role_delta_summary", ""),
        "domain_shift_signal": result.get("domain_shift_signal", False),
        "reflective_prompt": result.get("reflective_prompt", ""),
    }
