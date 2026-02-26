# test_tools.py
# Located in: /agent_core/
"""
🧪 Testing & Simulation Tools
-----------------------------
Purpose: Help agents run in standalone mode, generate mock inputs,
and simulate upstream/downstream agents for debugging.

Used by:
- Resume Agent → Test parsing edge cases
- Role Detail Agent → Simulate payloads from Resume + Aspiration
- Skill Delta Agent → Try downstream flow with missing fields

"""

import random
from datetime import datetime

MOCK_TITLES = ["Product Manager", "UX Designer", "Data Analyst"]
MOCK_DOMAINS = ["healthcare", "e-commerce", "logistics"]
MOCK_TASKS = ["roadmap planning", "KPI reporting", "cross-functional meetings"]


def mock_upstream_context(role_title="Product Manager"):
    return {
        "title": role_title,
        "seniority": "Mid-Senior IC",
        "domain": random.choice(MOCK_DOMAINS),
        "tools": ["Jira", "Notion", "ChatGPT"],
        "company_size": 500,
        "goal": "Become an AI-savvy PM"
    }


def simulate_downstream_usage(output_dict):
    return {
        "skill_delta_agent_input": {
            "known_skills": output_dict.get("skills", []),
            "task_clusters": output_dict.get("task_clusters", {})
        },
        "meta_agent_feedback": {
            "rating": random.choice([3, 4, 5]),
            "timestamp": str(datetime.utcnow())
        }
    }


def auto_generate_edge_case_inputs():
    return {
        "resume":
        "Worked at unknown startup doing everything. No tools mentioned.",
        "aspiration": "want to build LLM apps",
        "linkedin": "follow OpenAI, Anthropic; no recent posts"
    }


def visualize_agent_io_path(agent_name, inputs, outputs):
    return {
        "agent": agent_name,
        "input_summary": list(inputs.keys()),
        "output_fields": list(outputs.keys()),
        "timestamp": str(datetime.utcnow())
    }
