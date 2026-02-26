# downstream_formatter.py
# Located in: /agent_core/
"""
📦 Downstream Formatter Utilities
----------------------------------
Purpose: Help agents prepare their outputs in a structured, reusable format
for downstream agents like Gap Analysis, Tool Recommender, or Meta Agent.
Ensures consistent field naming, schema tagging, and payload simplification.

Used by:
- Role Detail Agent → sends task_clusters and effort_distribution to Skill Delta Agent
- Resume Agent → sends title, tools, domain to Role Context Agent
- Skill Delta Agent → sends missing skills to Learning Path Agent

"""


def format_for_agent(agent_name, full_output_dict):
    """
    Returns a tailored payload for a given downstream agent
    """
    formatted_payloads = {
        "gap_analysis_agent": {
            "task_clusters":
            full_output_dict.get("task_clusters"),
            "effort_distribution":
            full_output_dict.get("effort_distribution"),
            "ai_opportunity_density":
            full_output_dict.get("ai_opportunity_density"),
        },
        "skill_delta_agent": {
            "task_clusters": full_output_dict.get("task_clusters"),
            "skill_tags": full_output_dict.get("skill_tags"),
        },
        "meta_agent": {
            "summary": full_output_dict.get("summary"),
            "highlights": full_output_dict.get("highlight_insights"),
        },
        "learning_path_agent": {
            "missing_skills": full_output_dict.get("missing_skills"),
            "domain": full_output_dict.get("domain"),
            "role": full_output_dict.get("title"),
        }
    }
    return formatted_payloads.get(agent_name, {})


def standardize_payload_structure(output_dict, required_fields):
    """
    Creates a minimal dict with only required fields and tags missing fields
    """
    payload = {}
    for field in required_fields:
        payload[field] = output_dict.get(field, None)
    return payload


def tag_downstream_fields(fields_dict):
    """
    Tags each field with a list of downstream agents that use it
    """
    field_usage = {
        "title": ["role_context_agent", "role_ladder_agent"],
        "domain": ["gap_analysis_agent", "skill_delta_agent"],
        "task_clusters": ["gap_analysis_agent", "skill_delta_agent"],
        "tools": ["tool_familiarity_agent"],
        "ai_opportunity_density": ["meta_agent"]
    }
    return {
        field: {
            "value": value,
            "used_by": field_usage.get(field, [])
        }
        for field, value in fields_dict.items()
    }
