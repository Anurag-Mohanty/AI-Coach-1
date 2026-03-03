"""
analyze_role tool — wraps role_context_agent.analyze_role_context().
Returns role archetype, org shape, AI applicability constraints, confidence.
Uses asyncio.run() since role_context_agent is async.
"""
import asyncio
import re

from tools.role_context_agent.role_context_agent import analyze_role_context


def analyze_role(
    title: str,
    company: str = "",
    domain: str = "",
    seniority: str = "",
    company_size: str = "",
) -> dict:
    """
    Analyze role context — archetype, AI applicability, org shape.
    Input:  role details as individual fields
    Output: simplified role context dict with role_archetype, org_shape,
            ai_applicability_constraints, confidence
    """
    input_bundle = {
        "title": title or "Not specified",
        "company": company or "Not specified",
        "domain": domain or "Not specified",
        "seniority": seniority or "Not specified",
        "company_size": company_size or "Not specified",
    }

    try:
        result = asyncio.run(analyze_role_context(input_bundle))
    except RuntimeError:
        # Event loop already running (e.g. in some test environments)
        # Fall back to creating a new loop
        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(analyze_role_context(input_bundle))
        finally:
            loop.close()

    if "error" in result:
        return result

    # role_context_agent returns {full_output, role_context, downstream_payloads}
    # We expose the role_context dict directly for the coordinator
    role_context = result.get("role_context") or result.get("full_output") or result
    return {
        "role_archetype": role_context.get("contextualized_role_type", ""),
        "role_archetype_tag": role_context.get("role_archetype_tag", ""),
        "org_shape": role_context.get("org_shape_inference", ""),
        "cross_functional_density": role_context.get("cross_functional_density", ""),
        "ai_applicability": role_context.get("ops_or_strategy_bias", ""),
        "ai_applicability_constraints": role_context.get("ai_applicability_constraints", ""),
        "confidence": role_context.get("confidence_score", 0.8),
    }
