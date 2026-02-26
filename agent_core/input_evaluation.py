# input_evaluation.py
# Located in: /agent_core/
"""
🧪 Input Evaluation Utilities
-----------------------------
Purpose: Help agents assess the quality and completeness of the input they receive.
Useful for feedback loops to Resume Agent, LinkedIn Agent, or Aspirations.

Used by:
- Role Detail Agent → detects vague or missing task clusters
- Skill Delta Agent → identifies missing target role
- Meta Agent → compares clarity across user personas
- Learning Path Agent → validates input completeness

"""


def validate_inputs(inputs):
    """
    Validate that required inputs exist and are non-empty
    Used by multiple agents for basic input validation
    """
    if not inputs or not isinstance(inputs, (list, dict)):
        return False
    if isinstance(inputs, list) and not all(inputs):
        return False
    if isinstance(inputs, dict) and not all(inputs.values()):
        return False
    return True


def evaluate_input_completeness(output_dict, required_fields):
    missing_fields = [
        field for field in required_fields if not output_dict.get(field)
    ]
    return {
        "missing_fields": missing_fields,
        "is_complete": len(missing_fields) == 0
    }


def detect_missing_context(context_dict):
    weak_signals = []
    if not context_dict.get("role"):
        weak_signals.append("Missing role title")
    if not context_dict.get("resume"):
        weak_signals.append("No resume uploaded")
    if not context_dict.get("aspiration"):
        weak_signals.append("Missing future goal")
    return {
        "weak_context_signals":
        weak_signals,
        "signal_strength":
        "low"
        if len(weak_signals) >= 2 else "medium" if weak_signals else "high"
    }


def score_input_clarity(input_dict):
    score = 1.0
    if not input_dict.get("task_clusters"):
        score -= 0.3
    if not input_dict.get("effort_distribution"):
        score -= 0.3
    if not input_dict.get("skill_tags"):
        score -= 0.3
    return round(score, 2)
