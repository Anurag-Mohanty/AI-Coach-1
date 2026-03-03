# trust_explainability.py
# Located in: /agent_core/
"""
🔎 Trust & Explainability
---------------------------
Purpose: Help users understand how an agent generated its output —
which fields are confident vs. weak, and what logic led to the conclusion.

Used by:
- Role Detail Agent → Explain "why these task clusters"
- Resume Agent → Flag "title" as weak if not matched with other signals
- Meta Agent → Show reasoning tree across agents

"""

from typing import Dict
from agent_core.agent_logger import log_agent_event
from agent_core.self_learning import learn_from_feedback


def generate_why_this_output_summary(agent_name: str, input_summary: str,
                                     rules_used: list,
                                     model_confidence: float) -> str:
    """
    Create a paragraph explaining the basis of an agent's conclusion
    """
    return (
        f"Based on the provided input, the {agent_name.replace('_', ' ').title()} used the following rules: {', '.join(rules_used)}. "
        f"The overall model confidence in the accuracy of this result is "
        f"{round(model_confidence * 100) if isinstance(model_confidence, (int, float)) else model_confidence}%. "
        f"This summary was based on: {input_summary}")


def highlight_confidence_levels(
        fields_dict: Dict[str, Dict]) -> Dict[str, Dict]:
    """
    Add a confidence label to each output field
    """
    for field, details in fields_dict.items():
        score = details.get("confidence", 0.8)  # default 80%
        if score > 0.85:
            details["confidence_level"] = "high"
        elif score > 0.6:
            details["confidence_level"] = "medium"
        else:
            details["confidence_level"] = "low"
    return fields_dict


def display_reasoning_path(agent_name: str, intermediate_steps: list) -> str:
    """
    Describe the agent's reasoning journey step-by-step
    """
    path = " → ".join(intermediate_steps)
    return f"{agent_name.replace('_', ' ').title()} reasoning path: {path}"


def offer_counterfactuals(field_name: str, alternative_value: str,
                          potential_change: str) -> str:
    """
    Provide a "what-if" scenario to help user understand decision boundaries
    """
    return f"If your '{field_name}' had been '{alternative_value}', we would likely have recommended: {potential_change}."

def explain_why_included(agent: str, output_block: str, rationale: str) -> None:
    """
    Document why a specific output block was included in the agent's response
    """
    log_agent_event(f"{agent}.Explainability", f"Block rationale: {rationale}")
